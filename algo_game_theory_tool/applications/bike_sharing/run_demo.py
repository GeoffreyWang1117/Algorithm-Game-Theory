"""
Citi Bike 再平衡系统 - 完整演示

演示端到端流程：
1. 模拟数据生成（如果无真实数据）
2. 需求预测
3. 激励优化
4. 结果可视化
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

from incentive_optimizer import IncentiveOptimizer, Station


class BikeShareSimulator:
    """共享单车系统模拟器"""

    def __init__(self, num_stations=20, seed=42):
        self.num_stations = num_stations
        self.rng = np.random.RandomState(seed)

        # 生成模拟站点
        self.stations = self._generate_stations()

    def _generate_stations(self):
        """生成模拟站点"""
        stations = []

        for i in range(self.num_stations):
            capacity = self.rng.randint(40, 120)

            # 模拟不同类型的站点
            station_type = self.rng.choice(['residential', 'commercial', 'transit', 'tourist'])

            if station_type == 'residential':
                # 住宅区：早上满，晚上空
                util = 0.8 if datetime.now().hour < 12 else 0.2
            elif station_type == 'commercial':
                # 商业区：早上空，晚上满
                util = 0.2 if datetime.now().hour < 12 else 0.8
            elif station_type == 'transit':
                # 交通枢纽：波动大
                util = self.rng.uniform(0.1, 0.9)
            else:  # tourist
                # 旅游点：中等利用率
                util = self.rng.uniform(0.3, 0.7)

            current_bikes = int(capacity * util)

            # 预测净流量
            if station_type == 'residential':
                net_flow = -self.rng.randint(5, 15)  # 流出
            elif station_type == 'commercial':
                net_flow = self.rng.randint(5, 15)   # 流入
            else:
                net_flow = self.rng.randint(-10, 10)

            station = Station(
                station_id=f'station_{i:02d}_{station_type}',
                capacity=capacity,
                current_bikes=current_bikes,
                net_flow_forecast=net_flow
            )

            stations.append(station)

        return stations

    def simulate_day(self, optimizer, hours=24):
        """
        模拟一天的运营

        参数:
            optimizer: IncentiveOptimizer instance
            hours: 模拟小时数

        返回:
            dict: Simulation results
        """
        results = {
            'hourly_data': [],
            'total_cost': 0,
            'total_savings': 0,
            'user_participation': 0
        }

        for hour in range(hours):
            print(f"\n--- Hour {hour:02d}:00 ---")

            # 优化激励
            incentives, sim = optimizer.optimize(self.stations)

            # 记录结果
            results['hourly_data'].append({
                'hour': hour,
                'participants': sim['total_participants'],
                'cost': sim['total_cost'],
                'savings': sim['net_savings'],
                'roi': sim['roi']
            })

            results['total_cost'] += sim['total_cost']
            results['total_savings'] += sim['net_savings']
            results['user_participation'] += sim['total_participants']

            # 更新站点状态（模拟骑行）
            self._update_stations()

        return results

    def _update_stations(self):
        """更新站点状态（简化模拟）"""
        for station in self.stations:
            # 应用净流量
            new_bikes = station.current_bikes + station.net_flow_forecast

            # 限制在容量范围内
            station.current_bikes = np.clip(new_bikes, 0, station.capacity)

            # 更新预测（添加随机性）
            station.net_flow_forecast = self.rng.randint(-15, 15)


def visualize_results(results, output_dir='outputs/figures'):
    """可视化模拟结果"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(results['hourly_data'])

    # 1. 每小时成本和节省
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # ROI over time
    axes[0, 0].plot(df['hour'], df['roi'], marker='o', linewidth=2)
    axes[0, 0].axhline(y=1.0, color='r', linestyle='--', label='Break-even')
    axes[0, 0].set_xlabel('Hour of Day')
    axes[0, 0].set_ylabel('ROI')
    axes[0, 0].set_title('Return on Investment Over Time')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # Cost and Savings
    axes[0, 1].plot(df['hour'], df['cost'], marker='s', label='Incentive Cost', linewidth=2)
    axes[0, 1].plot(df['hour'], df['savings'], marker='^', label='Net Savings', linewidth=2)
    axes[0, 1].set_xlabel('Hour of Day')
    axes[0, 1].set_ylabel('Cost/Savings ($)')
    axes[0, 1].set_title('Hourly Cost and Savings')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    # Cumulative savings
    df['cumulative_savings'] = df['savings'].cumsum()
    axes[1, 0].plot(df['hour'], df['cumulative_savings'], marker='o',
                   color='green', linewidth=2)
    axes[1, 0].fill_between(df['hour'], 0, df['cumulative_savings'],
                            alpha=0.3, color='green')
    axes[1, 0].set_xlabel('Hour of Day')
    axes[1, 0].set_ylabel('Cumulative Savings ($)')
    axes[1, 0].set_title('Cumulative Net Savings')
    axes[1, 0].grid(True, alpha=0.3)

    # User participation
    axes[1, 1].bar(df['hour'], df['participants'], color='steelblue', alpha=0.7)
    axes[1, 1].set_xlabel('Hour of Day')
    axes[1, 1].set_ylabel('Number of Participants')
    axes[1, 1].set_title('User Participation Over Time')
    axes[1, 1].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(f'{output_dir}/simulation_results.png', dpi=150, bbox_inches='tight')
    print(f"\n✓ 可视化结果保存至: {output_dir}/simulation_results.png")


def print_summary(results):
    """打印摘要报告"""
    print("\n" + "=" * 70)
    print("模拟摘要报告")
    print("=" * 70)

    print(f"\n总体指标:")
    print(f"  总激励成本: ${results['total_cost']:.2f}")
    print(f"  总节省成本: ${results['total_savings']:.2f}")
    print(f"  净收益: ${results['total_savings']:.2f}")
    print(f"  总参与人数: {results['user_participation']:.0f}")

    avg_roi = np.mean([h['roi'] for h in results['hourly_data']])
    print(f"  平均ROI: {avg_roi:.2f}x")

    # 高峰vs非高峰对比
    df = pd.DataFrame(results['hourly_data'])
    peak_hours = df[df['hour'].isin(range(7, 10)).tolist() + df['hour'].isin(range(17, 21)).tolist()]
    off_peak = df[~df['hour'].isin(range(7, 10)).tolist() + ~df['hour'].isin(range(17, 21)).tolist()]

    print(f"\n高峰时段 (7-9am, 5-8pm):")
    print(f"  平均ROI: {peak_hours['roi'].mean():.2f}x")
    print(f"  平均参与: {peak_hours['participants'].mean():.0f} 人/小时")

    print(f"\n非高峰时段:")
    print(f"  平均ROI: {off_peak['roi'].mean():.2f}x")
    print(f"  平均参与: {off_peak['participants'].mean():.0f} 人/小时")


def compare_strategies():
    """对比不同激励策略"""
    print("\n" + "=" * 70)
    print("激励策略对比")
    print("=" * 70)

    simulator = BikeShareSimulator(num_stations=20)

    strategies = ['static', 'dynamic']
    results_by_strategy = {}

    for strategy in strategies:
        print(f"\n运行策略: {strategy}")
        print("-" * 70)

        optimizer = IncentiveOptimizer()
        optimizer.strategy = strategy

        # 重置模拟器
        simulator = BikeShareSimulator(num_stations=20, seed=42)

        # 运行模拟（简化：只模拟6小时）
        results = simulator.simulate_day(optimizer, hours=6)

        results_by_strategy[strategy] = results

    # 对比
    print("\n" + "=" * 70)
    print("策略对比结果")
    print("=" * 70)

    comparison_data = []
    for strategy, results in results_by_strategy.items():
        avg_roi = np.mean([h['roi'] for h in results['hourly_data']])
        comparison_data.append({
            '策略': strategy,
            '总成本': results['total_cost'],
            '总节省': results['total_savings'],
            '平均ROI': avg_roi,
            '总参与': results['user_participation']
        })

    comparison_df = pd.DataFrame(comparison_data)
    print(comparison_df.to_string(index=False))

    # 可视化对比
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].bar(comparison_df['策略'], comparison_df['平均ROI'], color=['skyblue', 'coral'])
    axes[0].set_ylabel('Average ROI')
    axes[0].set_title('ROI Comparison')
    axes[0].axhline(y=1.0, color='r', linestyle='--', label='Break-even')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3, axis='y')

    axes[1].bar(comparison_df['策略'], comparison_df['总节省'], color=['skyblue', 'coral'])
    axes[1].set_ylabel('Total Savings ($)')
    axes[1].set_title('Total Savings Comparison')
    axes[1].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('outputs/figures/strategy_comparison.png', dpi=150, bbox_inches='tight')
    print(f"\n✓ 策略对比图保存至: outputs/figures/strategy_comparison.png")


def main():
    """主演示程序"""
    print("=" * 70)
    print("Citi Bike 再平衡系统 - 完整演示")
    print("=" * 70)

    print("\n本演示将展示：")
    print("  1. 模拟共享单车系统运营")
    print("  2. 应用博弈论激励机制")
    print("  3. 对比不同优化策略")
    print("  4. 可视化结果分析")

    input("\n按 Enter 开始演示...")

    # 1. 基础演示
    print("\n" + "=" * 70)
    print("1. 基础演示：动态定价策略")
    print("=" * 70)

    simulator = BikeShareSimulator(num_stations=20)
    optimizer = IncentiveOptimizer()
    optimizer.strategy = 'dynamic'

    # 运行6小时模拟
    results = simulator.simulate_day(optimizer, hours=6)

    # 打印摘要
    print_summary(results)

    # 可视化
    visualize_results(results)

    # 2. 策略对比
    compare_strategies()

    print("\n" + "=" * 70)
    print("✓ 演示完成！")
    print("=" * 70)

    print("\n查看结果：")
    print("  - 可视化图表: outputs/figures/")
    print("  - 模拟数据: outputs/simulation_results.csv")

    # 保存模拟数据
    output_dir = Path('outputs')
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(results['hourly_data'])
    df.to_csv('outputs/simulation_results.csv', index=False)
    print("  ✓ 数据已保存")


if __name__ == '__main__':
    # 设置绘图样式
    sns.set_style('whitegrid')
    plt.rcParams['figure.figsize'] = (12, 6)
    plt.rcParams['font.size'] = 10

    main()
