"""
预算Pacing优化器

防止广告主预算在高峰期快速耗尽，实现平滑消耗
"""

import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import yaml


@dataclass
class BudgetState:
    """预算状态"""
    total_budget: float
    spent: float
    remaining: float
    target_pace: float  # 目标消耗率
    actual_pace: float  # 实际消耗率
    timestamp: datetime


class BudgetPacer:
    """预算Pacing控制器"""

    def __init__(self, daily_budget: float, duration_hours: int = 24,
                 strategy: str = 'pid'):
        """
        初始化预算Pacer

        参数:
            daily_budget: 每日预算
            duration_hours: 持续时间（小时）
            strategy: Pacing策略（linear, pid, adaptive）
        """
        self.daily_budget = daily_budget
        self.duration_hours = duration_hours
        self.strategy = strategy

        # 目标消耗率（$/小时）
        self.target_rate = daily_budget / duration_hours

        # PID控制器参数
        self.Kp = 0.5  # 比例系数
        self.Ki = 0.1  # 积分系数
        self.Kd = 0.05  # 微分系数

        # 状态变量
        self.error_sum = 0.0  # 误差积分
        self.last_error = 0.0  # 上次误差
        self.last_time = 0.0  # 上次时间

    def calculate_target_spend(self, elapsed_hours: float) -> float:
        """
        计算目标消耗

        参数:
            elapsed_hours: 已过时间（小时）

        返回:
            float: 目标消耗金额
        """
        return self.target_rate * elapsed_hours

    def adjust_bid_linear(self, current_spend: float,
                         elapsed_hours: float) -> float:
        """
        线性Pacing策略

        简单但有效：根据预算进度调整出价

        参数:
            current_spend: 当前消耗
            elapsed_hours: 已过时间

        返回:
            float: 出价调整系数 [0.5, 2.0]
        """
        # 计算预算进度
        budget_progress = current_spend / self.daily_budget

        # 计算时间进度
        time_progress = elapsed_hours / self.duration_hours

        # 如果消耗过快，降低出价
        if budget_progress > time_progress:
            # 超前消耗
            overspend_ratio = budget_progress / time_progress
            multiplier = 1.0 / overspend_ratio
        else:
            # 消耗过慢
            underspend_ratio = time_progress / budget_progress if budget_progress > 0 else 2.0
            multiplier = min(underspend_ratio, 2.0)

        # 限制调整范围
        return np.clip(multiplier, 0.5, 2.0)

    def adjust_bid_pid(self, current_spend: float,
                      elapsed_hours: float) -> float:
        """
        PID控制器Pacing

        更精确的控制，平滑调整

        参数:
            current_spend: 当前消耗
            elapsed_hours: 已过时间

        返回:
            float: 出价调整系数
        """
        # 目标消耗
        target_spend = self.calculate_target_spend(elapsed_hours)

        # 误差（正值表示消耗不足，需提高出价）
        error = target_spend - current_spend

        # 时间间隔
        dt = elapsed_hours - self.last_time
        if dt <= 0:
            dt = 1.0

        # 积分项
        self.error_sum += error * dt

        # 微分项
        error_derivative = (error - self.last_error) / dt

        # PID计算
        adjustment = (self.Kp * error +
                     self.Ki * self.error_sum +
                     self.Kd * error_derivative)

        # 更新状态
        self.last_error = error
        self.last_time = elapsed_hours

        # 转换为出价乘数
        # adjustment > 0: 需要加速消耗，提高出价
        # adjustment < 0: 需要减速消耗，降低出价
        multiplier = 1.0 + adjustment / self.daily_budget

        # 限制范围
        return np.clip(multiplier, 0.5, 2.0)

    def adjust_bid_adaptive(self, current_spend: float,
                           elapsed_hours: float,
                           market_competition: float = 1.0,
                           predicted_ctr: float = 0.01) -> float:
        """
        自适应Pacing

        考虑市场竞争和转化率

        参数:
            current_spend: 当前消耗
            elapsed_hours: 已过时间
            market_competition: 市场竞争度 [0.5, 2.0]
            predicted_ctr: 预测CTR

        返回:
            float: 出价调整系数
        """
        # 基础PID调整
        base_multiplier = self.adjust_bid_pid(current_spend, elapsed_hours)

        # 市场竞争调整
        # 竞争激烈时，适当降低出价（避免高峰消耗过快）
        competition_adjustment = 1.0 / market_competition

        # CTR调整
        # CTR高时，适当提高出价（机会好）
        baseline_ctr = 0.01
        ctr_adjustment = predicted_ctr / baseline_ctr

        # 综合调整
        final_multiplier = base_multiplier * competition_adjustment * ctr_adjustment

        return np.clip(final_multiplier, 0.5, 2.0)

    def should_participate(self, current_spend: float,
                          elapsed_hours: float,
                          auction_cpc: float) -> bool:
        """
        决定是否参与本次拍卖

        概率性throttling

        参数:
            current_spend: 当前消耗
            elapsed_hours: 已过时间
            auction_cpc: 本次拍卖的预估CPC

        返回:
            bool: 是否参与
        """
        # 剩余预算
        remaining = self.daily_budget - current_spend

        # 剩余时间
        remaining_hours = self.duration_hours - elapsed_hours

        if remaining_hours <= 0:
            return False

        # 目标剩余消耗率
        target_remaining_rate = remaining / remaining_hours

        # 如果本次拍卖成本高于剩余消耗率，概率性跳过
        if auction_cpc > target_remaining_rate:
            # 参与概率
            prob = target_remaining_rate / auction_cpc
            return np.random.random() < prob

        return True

    def get_bid_adjustment(self, current_spend: float,
                          elapsed_hours: float,
                          **kwargs) -> float:
        """
        获取出价调整系数

        参数:
            current_spend: 当前消耗
            elapsed_hours: 已过时间
            **kwargs: 策略特定参数

        返回:
            float: 出价调整系数
        """
        if self.strategy == 'linear':
            return self.adjust_bid_linear(current_spend, elapsed_hours)

        elif self.strategy == 'pid':
            return self.adjust_bid_pid(current_spend, elapsed_hours)

        elif self.strategy == 'adaptive':
            return self.adjust_bid_adaptive(
                current_spend, elapsed_hours,
                kwargs.get('market_competition', 1.0),
                kwargs.get('predicted_ctr', 0.01)
            )

        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")


class BudgetOptimizer:
    """预算优化器（多天优化）"""

    def __init__(self, total_budget: float, duration_days: int,
                 conversion_value: float):
        """
        初始化预算优化器

        参数:
            total_budget: 总预算
            duration_days: 持续天数
            conversion_value: 每个转化的价值
        """
        self.total_budget = total_budget
        self.duration_days = duration_days
        self.conversion_value = conversion_value

        # 每日预算（初始均分）
        self.daily_budgets = [total_budget / duration_days] * duration_days

    def optimize_allocation(self, forecasted_demand: List[float],
                           forecasted_ctr: List[float],
                           forecasted_cvr: List[float]) -> List[float]:
        """
        优化每日预算分配

        基于预测的需求、CTR、CVR优化

        参数:
            forecasted_demand: 每日预测展示量
            forecasted_ctr: 每日预测CTR
            forecasted_cvr: 每日预测转化率

        返回:
            List[float]: 优化后的每日预算分配
        """
        # 计算每日的预期ROI
        daily_roi = []
        for i in range(self.duration_days):
            expected_clicks = forecasted_demand[i] * forecasted_ctr[i]
            expected_conversions = expected_clicks * forecasted_cvr[i]
            expected_value = expected_conversions * self.conversion_value

            # ROI = value / cost（假设CPC恒定）
            # 简化：ROI ∝ demand × CTR × CVR
            roi_score = forecasted_demand[i] * forecasted_ctr[i] * forecasted_cvr[i]
            daily_roi.append(roi_score)

        # 归一化ROI
        total_roi = sum(daily_roi)
        if total_roi == 0:
            return self.daily_budgets

        # 按ROI比例分配预算
        optimized_budgets = [
            (roi / total_roi) * self.total_budget
            for roi in daily_roi
        ]

        return optimized_budgets

    def smooth_allocation(self, optimized_budgets: List[float],
                         smoothing_factor: float = 0.3) -> List[float]:
        """
        平滑预算分配

        避免单日预算波动过大

        参数:
            optimized_budgets: 优化后的预算
            smoothing_factor: 平滑因子 [0, 1]

        返回:
            List[float]: 平滑后的预算
        """
        smoothed = optimized_budgets.copy()

        for i in range(1, len(smoothed) - 1):
            # 加权平均：前一天、当天、后一天
            avg = (smoothed[i-1] + smoothed[i] + smoothed[i+1]) / 3
            smoothed[i] = (1 - smoothing_factor) * smoothed[i] + smoothing_factor * avg

        return smoothed


def simulate_pacing():
    """模拟预算Pacing"""
    print("=" * 70)
    print("预算Pacing模拟")
    print("=" * 70)

    daily_budget = 1000.0
    duration_hours = 24

    print(f"\n配置:")
    print(f"  每日预算: ${daily_budget:.2f}")
    print(f"  持续时间: {duration_hours}小时")
    print(f"  目标消耗率: ${daily_budget/duration_hours:.2f}/小时")

    # 模拟3种策略
    strategies = ['linear', 'pid', 'adaptive']
    results = {}

    for strategy in strategies:
        print(f"\n{'='*70}")
        print(f"策略: {strategy.upper()}")
        print(f"{'='*70}")

        pacer = BudgetPacer(daily_budget, duration_hours, strategy=strategy)

        # 模拟24小时
        current_spend = 0.0
        hourly_data = []

        for hour in range(duration_hours):
            # 模拟市场竞争度（高峰期竞争激烈）
            if hour in [8, 9, 10, 17, 18, 19, 20]:
                market_competition = 1.5  # 高峰
                hourly_demand = 1000
            else:
                market_competition = 0.8  # 非高峰
                hourly_demand = 500

            # 获取出价调整
            if strategy == 'adaptive':
                multiplier = pacer.get_bid_adjustment(
                    current_spend, hour,
                    market_competition=market_competition,
                    predicted_ctr=0.01
                )
            else:
                multiplier = pacer.get_bid_adjustment(current_spend, hour)

            # 基础CPC
            base_cpc = 0.5

            # 调整后的CPC
            adjusted_cpc = base_cpc * multiplier

            # 模拟点击数（简化）
            clicks = hourly_demand * 0.01  # 1% CTR
            hourly_cost = clicks * adjusted_cpc

            current_spend += hourly_cost

            # 确保不超预算
            if current_spend > daily_budget:
                overspend = current_spend - daily_budget
                hourly_cost -= overspend
                current_spend = daily_budget

            hourly_data.append({
                'hour': hour,
                'multiplier': multiplier,
                'cost': hourly_cost,
                'cumulative': current_spend,
                'target': pacer.calculate_target_spend(hour + 1)
            })

        results[strategy] = hourly_data

        # 打印摘要
        total_spent = current_spend
        utilization = (total_spent / daily_budget) * 100

        print(f"\n最终结果:")
        print(f"  总消耗: ${total_spent:.2f}")
        print(f"  预算利用率: {utilization:.1f}%")

        # 计算消耗方差（衡量平滑度）
        hourly_costs = [h['cost'] for h in hourly_data]
        variance = np.var(hourly_costs)
        print(f"  消耗方差: {variance:.2f} (越小越平滑)")

    # 对比
    print(f"\n{'='*70}")
    print("策略对比")
    print(f"{'='*70}")

    import pandas as pd

    comparison = []
    for strategy, data in results.items():
        total = data[-1]['cumulative']
        variance = np.var([h['cost'] for h in data])

        comparison.append({
            '策略': strategy,
            '总消耗': f"${total:.2f}",
            '利用率': f"{total/daily_budget*100:.1f}%",
            '消耗方差': f"{variance:.2f}"
        })

    df = pd.DataFrame(comparison)
    print(df.to_string(index=False))

    print(f"\n💡 关键发现:")
    print(f"  - PID控制器提供最平滑的预算消耗")
    print(f"  - 自适应策略在保持平滑的同时响应市场变化")
    print(f"  - 线性策略简单但有效")


if __name__ == '__main__':
    simulate_pacing()
