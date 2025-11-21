"""
广告拍卖系统 - 完整演示

展示端到端的广告拍卖流程：
1. 创建广告主和广告位
2. 运行GSP拍卖
3. 预算Pacing优化
4. 机制对比分析
5. 结果可视化
"""

import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

from gsp_auction import GSPAuction, VCGAuction, Advertiser, AdSlot
from budget_pacing import BudgetPacer


class AdAuctionSimulator:
    """广告拍卖模拟器"""

    def __init__(self, num_advertisers: int = 10, num_slots: int = 3,
                 seed: int = 42):
        """
        初始化模拟器

        参数:
            num_advertisers: 广告主数量
            num_slots: 广告位数量
            seed: 随机种子
        """
        self.num_advertisers = num_advertisers
        self.num_slots = num_slots
        self.rng = np.random.RandomState(seed)

        # 创建广告主
        self.advertisers = self._generate_advertisers()

        # 创建真实估值
        self.true_values = self._generate_true_values()

        # 创建广告位
        self.slots = self._generate_slots()

    def _generate_advertisers(self) -> list:
        """生成模拟广告主"""
        advertisers = []

        for i in range(self.num_advertisers):
            # 广告主类型
            adv_type = self.rng.choice(['brand', 'performance', 'small_business'])

            if adv_type == 'brand':
                budget = self.rng.uniform(5000, 50000)
                bid = self.rng.uniform(1.5, 3.5)
                quality = self.rng.uniform(0.7, 1.0)
            elif adv_type == 'performance':
                budget = self.rng.uniform(500, 5000)
                bid = self.rng.uniform(0.8, 2.0)
                quality = self.rng.uniform(0.5, 0.8)
            else:  # small_business
                budget = self.rng.uniform(100, 1000)
                bid = self.rng.uniform(0.3, 1.0)
                quality = self.rng.uniform(0.3, 0.7)

            advertiser = Advertiser(
                id=f'Adv_{i:02d}_{adv_type}',
                bid=bid,
                quality_score=quality,
                budget=budget
            )

            advertisers.append(advertiser)

        return advertisers

    def _generate_true_values(self) -> dict:
        """生成真实估值（通常高于出价）"""
        true_values = {}

        for adv in self.advertisers:
            # 真实估值 = 出价 × (1.1 到 1.5)
            multiplier = self.rng.uniform(1.1, 1.5)
            true_values[adv.id] = adv.bid * multiplier

        return true_values

    def _generate_slots(self) -> list:
        """生成广告位"""
        slots = []

        # 标准位置衰减
        ctr_multipliers = [1.0, 0.6, 0.3, 0.15, 0.08]

        for i in range(self.num_slots):
            slot = AdSlot(
                position=i + 1,
                ctr_multiplier=ctr_multipliers[min(i, len(ctr_multipliers) - 1)],
                base_ctr=0.05
            )
            slots.append(slot)

        return slots

    def simulate_day(self, mechanism: str = 'gsp',
                    use_pacing: bool = True,
                    impressions_per_hour: int = 1000) -> dict:
        """
        模拟一天的拍卖

        参数:
            mechanism: 拍卖机制（gsp或vcg）
            use_pacing: 是否使用预算pacing
            impressions_per_hour: 每小时展示量

        返回:
            dict: 模拟结果
        """
        # 创建拍卖
        if mechanism == 'gsp':
            auction = GSPAuction()
        elif mechanism == 'vcg':
            auction = VCGAuction(slots=self.slots, reserve_price=0.1)
        else:
            raise ValueError(f"Unknown mechanism: {mechanism}")

        # 如果使用pacing，为每个广告主创建pacer
        pacers = {}
        if use_pacing:
            for adv in self.advertisers:
                pacers[adv.id] = BudgetPacer(
                    daily_budget=adv.budget,
                    duration_hours=24,
                    strategy='pid'
                )

        # 重置广告主消耗
        for adv in self.advertisers:
            adv.daily_spend = 0.0

        # 模拟24小时
        hourly_results = []
        total_revenue = 0.0

        for hour in range(24):
            # 市场竞争度（高峰期更高）
            if hour in [8, 9, 10, 17, 18, 19, 20]:
                market_multiplier = 1.3
                impressions = int(impressions_per_hour * 1.5)
            else:
                market_multiplier = 0.8
                impressions = int(impressions_per_hour * 0.7)

            # 调整广告主出价（如果使用pacing）
            original_bids = {}
            if use_pacing:
                for adv in self.advertisers:
                    original_bids[adv.id] = adv.bid

                    pacer = pacers[adv.id]
                    multiplier = pacer.get_bid_adjustment(adv.daily_spend, hour)

                    # 应用调整
                    adv.bid = original_bids[adv.id] * multiplier

            # 运行拍卖
            if mechanism == 'gsp':
                results = auction.run(self.advertisers, impressions=impressions)
            else:  # vcg
                results = auction.run(self.advertisers, self.true_values,
                                     impressions=impressions)

            # 记录结果
            hour_revenue = sum(r.total_payment for r in results)
            hour_clicks = sum(r.expected_clicks for r in results)

            hourly_results.append({
                'hour': hour,
                'revenue': hour_revenue,
                'clicks': hour_clicks,
                'impressions': impressions,
                'num_winners': len(results)
            })

            total_revenue += hour_revenue

            # 恢复原始出价
            if use_pacing:
                for adv in self.advertisers:
                    adv.bid = original_bids[adv.id]

        # 汇总结果
        return {
            'mechanism': mechanism,
            'use_pacing': use_pacing,
            'total_revenue': total_revenue,
            'total_clicks': sum(h['clicks'] for h in hourly_results),
            'total_impressions': sum(h['impressions'] for h in hourly_results),
            'hourly_results': hourly_results,
            'advertiser_spends': {adv.id: adv.daily_spend for adv in self.advertisers}
        }


def visualize_results(results_by_config: dict, output_dir: str = 'outputs/figures'):
    """可视化模拟结果"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 1. 每小时收入对比
    ax = axes[0, 0]

    for config_name, results in results_by_config.items():
        hourly_data = results['hourly_results']
        hours = [h['hour'] for h in hourly_data]
        revenues = [h['revenue'] for h in hourly_data]

        ax.plot(hours, revenues, marker='o', label=config_name, linewidth=2)

    ax.set_xlabel('Hour of Day')
    ax.set_ylabel('Revenue ($)')
    ax.set_title('Hourly Revenue Comparison')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 2. 累积收入
    ax = axes[0, 1]

    for config_name, results in results_by_config.items():
        hourly_data = results['hourly_results']
        hours = [h['hour'] for h in hourly_data]
        cumulative = np.cumsum([h['revenue'] for h in hourly_data])

        ax.plot(hours, cumulative, marker='s', label=config_name, linewidth=2)

    ax.set_xlabel('Hour of Day')
    ax.set_ylabel('Cumulative Revenue ($)')
    ax.set_title('Cumulative Revenue Over Time')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 3. 总收入对比
    ax = axes[1, 0]

    configs = list(results_by_config.keys())
    revenues = [results_by_config[c]['total_revenue'] for c in configs]

    bars = ax.bar(range(len(configs)), revenues,
                  color=['skyblue', 'coral', 'lightgreen', 'gold'][:len(configs)])
    ax.set_xticks(range(len(configs)))
    ax.set_xticklabels(configs, rotation=15, ha='right')
    ax.set_ylabel('Total Revenue ($)')
    ax.set_title('Total Revenue Comparison')
    ax.grid(True, alpha=0.3, axis='y')

    # 在柱子上显示数值
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'${height:.0f}',
               ha='center', va='bottom')

    # 4. 收入分布（按小时方差）
    ax = axes[1, 1]

    variances = []
    for config_name, results in results_by_config.items():
        hourly_revenues = [h['revenue'] for h in results['hourly_results']]
        variance = np.std(hourly_revenues)
        variances.append(variance)

    bars = ax.bar(range(len(configs)), variances,
                  color=['skyblue', 'coral', 'lightgreen', 'gold'][:len(configs)])
    ax.set_xticks(range(len(configs)))
    ax.set_xticklabels(configs, rotation=15, ha='right')
    ax.set_ylabel('Revenue Std Dev ($)')
    ax.set_title('Revenue Stability (Lower = More Stable)')
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(f'{output_dir}/auction_comparison.png', dpi=150, bbox_inches='tight')
    print(f"\n✓ 可视化结果保存至: {output_dir}/auction_comparison.png")


def print_summary(results: dict):
    """打印结果摘要"""
    print(f"\n{'='*70}")
    print(f"模拟结果摘要: {results['mechanism'].upper()}")
    if results['use_pacing']:
        print("(使用预算Pacing)")
    print(f"{'='*70}")

    print(f"\n总体指标:")
    print(f"  总收入: ${results['total_revenue']:.2f}")
    print(f"  总点击数: {results['total_clicks']:.0f}")
    print(f"  总展示数: {results['total_impressions']:,}")
    print(f"  平均CPC: ${results['total_revenue'] / results['total_clicks']:.2f}")

    # 广告主消耗
    print(f"\n广告主消耗 (Top 5):")
    sorted_spends = sorted(results['advertiser_spends'].items(),
                          key=lambda x: x[1], reverse=True)[:5]

    for adv_id, spend in sorted_spends:
        print(f"  {adv_id}: ${spend:.2f}")


def main():
    """主演示程序"""
    print("=" * 70)
    print("广告拍卖系统 - 完整演示")
    print("=" * 70)

    print("\n本演示将展示：")
    print("  1. GSP vs VCG 拍卖机制对比")
    print("  2. 预算Pacing的效果")
    print("  3. 多配置性能分析")
    print("  4. 可视化结果")

    # 创建模拟器
    simulator = AdAuctionSimulator(num_advertisers=10, num_slots=3)

    print(f"\n模拟配置:")
    print(f"  广告主数量: {simulator.num_advertisers}")
    print(f"  广告位数量: {simulator.num_slots}")
    print(f"  模拟时长: 24小时")

    # 运行多种配置
    configs = [
        ('GSP (No Pacing)', 'gsp', False),
        ('GSP (With Pacing)', 'gsp', True),
        ('VCG (No Pacing)', 'vcg', False),
        ('VCG (With Pacing)', 'vcg', True),
    ]

    results_by_config = {}

    for config_name, mechanism, use_pacing in configs:
        print(f"\n{'='*70}")
        print(f"运行配置: {config_name}")
        print(f"{'='*70}")

        results = simulator.simulate_day(
            mechanism=mechanism,
            use_pacing=use_pacing,
            impressions_per_hour=1000
        )

        results_by_config[config_name] = results

        print_summary(results)

    # 对比分析
    print(f"\n{'='*70}")
    print("配置对比")
    print(f"{'='*70}")

    comparison_data = []
    for config_name, results in results_by_config.items():
        comparison_data.append({
            '配置': config_name,
            '总收入': f"${results['total_revenue']:.2f}",
            '总点击': f"{results['total_clicks']:.0f}",
            '平均CPC': f"${results['total_revenue']/results['total_clicks']:.2f}"
        })

    df = pd.DataFrame(comparison_data)
    print(df.to_string(index=False))

    # 可视化
    visualize_results(results_by_config)

    # 保存结果
    print(f"\n{'='*70}")
    print("保存结果")
    print(f"{'='*70}")

    output_dir = Path('outputs')
    output_dir.mkdir(parents=True, exist_ok=True)

    # 保存汇总
    df.to_csv('outputs/simulation_summary.csv', index=False)
    print("  ✓ 汇总数据: outputs/simulation_summary.csv")

    # 保存详细结果
    for config_name, results in results_by_config.items():
        hourly_df = pd.DataFrame(results['hourly_results'])
        filename = config_name.replace(' ', '_').replace('(', '').replace(')', '').lower()
        hourly_df.to_csv(f'outputs/{filename}_hourly.csv', index=False)

    print("  ✓ 详细数据: outputs/*_hourly.csv")

    print(f"\n{'='*70}")
    print("✓ 演示完成！")
    print(f"{'='*70}")

    print("\n查看结果：")
    print("  - 可视化图表: outputs/figures/auction_comparison.png")
    print("  - 汇总数据: outputs/simulation_summary.csv")
    print("  - 详细数据: outputs/*_hourly.csv")

    # 关键洞察
    print(f"\n💡 关键洞察:")

    gsp_no_pacing = results_by_config['GSP (No Pacing)']['total_revenue']
    gsp_with_pacing = results_by_config['GSP (With Pacing)']['total_revenue']
    vcg_no_pacing = results_by_config['VCG (No Pacing)']['total_revenue']

    print(f"  1. GSP vs VCG收入差异: "
          f"${gsp_no_pacing - vcg_no_pacing:.2f} "
          f"({(gsp_no_pacing/vcg_no_pacing - 1)*100:.1f}%)")

    print(f"  2. Pacing的影响: "
          f"${gsp_with_pacing - gsp_no_pacing:.2f} "
          f"({(gsp_with_pacing/gsp_no_pacing - 1)*100:.1f}%)")

    print(f"  3. VCG更真实，但收入较低")
    print(f"  4. Pacing提高预算利用率，增加总收入")


if __name__ == '__main__':
    # 设置绘图样式
    sns.set_style('whitegrid')
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 10

    main()
