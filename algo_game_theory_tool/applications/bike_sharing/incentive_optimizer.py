"""
共享单车激励优化器

基于博弈论的激励机制设计：
1. 静态定价（Simple & Fast）
2. 动态定价（Predictive）
3. 优化求解（CVXPY）
4. 用户响应模拟
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import yaml
import json

try:
    import cvxpy as cp
    CVXPY_AVAILABLE = True
except ImportError:
    CVXPY_AVAILABLE = False
    print("Warning: cvxpy not installed. Advanced optimization unavailable.")

from scipy.optimize import minimize
from scipy.special import expit  # sigmoid function


class Station:
    """站点状态"""

    def __init__(self, station_id, capacity, current_bikes, net_flow_forecast=0):
        self.id = station_id
        self.capacity = capacity
        self.current_bikes = current_bikes
        self.net_flow_forecast = net_flow_forecast

    @property
    def utilization(self):
        """当前利用率"""
        return self.current_bikes / self.capacity if self.capacity > 0 else 0.5

    @property
    def future_bikes(self):
        """预测的未来单车数"""
        return np.clip(self.current_bikes + self.net_flow_forecast, 0, self.capacity)

    @property
    def future_utilization(self):
        """预测的未来利用率"""
        return self.future_bikes / self.capacity if self.capacity > 0 else 0.5

    def is_deficit(self, threshold=0.2):
        """是否缺车"""
        return self.utilization < threshold

    def is_surplus(self, threshold=0.8):
        """是否满车"""
        return self.utilization > threshold

    def imbalance_score(self, current_weight=0.6, future_weight=0.4):
        """
        不平衡评分

        返回:
            float: 正值表示缺车，负值表示满车，0表示平衡
        """
        current_imb = 0.5 - self.utilization
        future_imb = 0.5 - self.future_utilization

        return current_weight * current_imb + future_weight * future_imb


class UserResponseModel:
    """用户响应模型"""

    def __init__(self, config):
        self.config = config

        # Logistic 模型参数
        self.beta_reward = config['beta_reward']
        self.beta_time = config['beta_time']
        self.beta_inconvenience = config['beta_inconvenience']

    def probability_accept(self, reward, detour_time):
        """
        计算用户接受激励的概率

        参数:
            reward: 奖励金额（美元）
            detour_time: 绕行时间（分钟）

        返回:
            float: 接受概率 [0, 1]
        """
        # 效用函数: U = β₁*reward - β₂*detour_time - β₃
        utility = (self.beta_reward * reward -
                  self.beta_time * detour_time -
                  self.beta_inconvenience)

        # Logistic 转换
        prob = expit(utility)

        return prob

    def expected_participants(self, num_users, reward, avg_detour_time):
        """
        预期参与人数

        参数:
            num_users: 潜在用户数
            reward: 奖励
            avg_detour_time: 平均绕行时间

        返回:
            float: 预期参与人数
        """
        prob = self.probability_accept(reward, avg_detour_time)
        return num_users * prob


class IncentiveOptimizer:
    """激励优化器"""

    def __init__(self, config_path='configs/incentive_config.yaml'):
        """初始化优化器"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.strategy = self.config['strategy']
        self.daily_budget = self.config['budget']['daily_budget']
        self.rebalancing_cost = self.config['operations']['rebalancing_cost']

        self.user_model = UserResponseModel(self.config['user_model'])

    def static_pricing(self, stations):
        """
        静态定价策略

        简单但有效：根据站点当前状态给予固定奖励

        参数:
            stations: List[Station]

        返回:
            dict: {station_id: {'reward': float, 'action': str}}
        """
        base_reward = self.config['static_pricing']['base_reward']
        deficit_mult = self.config['static_pricing']['deficit_multiplier']
        surplus_mult = self.config['static_pricing']['surplus_multiplier']

        incentives = {}

        for station in stations:
            if station.is_deficit():
                # 缺车站：鼓励还车
                degree = (0.2 - station.utilization) / 0.2
                reward = base_reward * deficit_mult * degree
                action = 'return'

            elif station.is_surplus():
                # 满车站：鼓励借车
                degree = (station.utilization - 0.8) / 0.2
                reward = base_reward * surplus_mult * degree
                action = 'pickup'

            else:
                # 正常站点：无激励
                reward = 0.0
                action = 'none'

            # 限制奖励范围
            reward = np.clip(reward,
                           self.config['budget']['min_reward'],
                           self.config['budget']['max_reward'])

            incentives[station.id] = {
                'reward': reward,
                'action': action,
                'utilization': station.utilization
            }

        return incentives

    def dynamic_pricing(self, stations):
        """
        动态定价策略

        考虑当前状态和未来预测

        参数:
            stations: List[Station]

        返回:
            dict: {station_id: {'reward': float, 'action': str}}
        """
        current_weight = self.config['dynamic_pricing']['current_weight']
        future_weight = self.config['dynamic_pricing']['future_weight']

        incentives = {}

        for station in stations:
            # 综合不平衡评分
            imbalance = station.imbalance_score(current_weight, future_weight)

            # 根据不平衡程度计算奖励
            if imbalance > 0.1:  # 缺车
                action = 'return'
                reward = self.config['static_pricing']['base_reward'] * abs(imbalance) * 2
            elif imbalance < -0.1:  # 满车
                action = 'pickup'
                reward = self.config['static_pricing']['base_reward'] * abs(imbalance) * 2
            else:
                action = 'none'
                reward = 0.0

            # 限制范围
            reward = np.clip(reward,
                           self.config['budget']['min_reward'],
                           self.config['budget']['max_reward'])

            incentives[station.id] = {
                'reward': reward,
                'action': action,
                'imbalance_score': imbalance,
                'current_util': station.utilization,
                'future_util': station.future_utilization
            }

        return incentives

    def optimize_with_cvxpy(self, stations, expected_users):
        """
        使用凸优化求解最优激励

        优化问题:
            minimize: total_cost
            subject to:
                - Budget constraint
                - Capacity constraints
                - Incentive compatibility

        参数:
            stations: List[Station]
            expected_users: Dict[station_id, num_users]

        返回:
            dict: Optimal incentives
        """
        if not CVXPY_AVAILABLE:
            print("CVXPY not available. Using dynamic pricing instead.")
            return self.dynamic_pricing(stations)

        n = len(stations)

        # 决策变量：每个站点的奖励
        rewards = cp.Variable(n)

        # 目标函数：最小化总成本
        # total_cost = incentive_cost + rebalancing_cost

        # 简化：假设奖励与参与人数成正比
        incentive_cost = cp.sum(rewards)

        # 约束
        constraints = []

        # 1. 预算约束
        constraints.append(cp.sum(rewards) <= self.daily_budget)

        # 2. 奖励范围
        constraints.append(rewards >= self.config['budget']['min_reward'])
        constraints.append(rewards <= self.config['budget']['max_reward'])

        # 3. 非负约束
        constraints.append(rewards >= 0)

        # 优化目标：最小化成本
        objective = cp.Minimize(incentive_cost)

        # 求解
        problem = cp.Problem(objective, constraints)

        try:
            problem.solve(solver=cp.ECOS, verbose=False)

            if problem.status == cp.OPTIMAL:
                optimal_rewards = rewards.value

                incentives = {}
                for i, station in enumerate(stations):
                    reward = optimal_rewards[i]

                    # 确定动作
                    if station.is_deficit():
                        action = 'return'
                    elif station.is_surplus():
                        action = 'pickup'
                    else:
                        action = 'none'

                    incentives[station.id] = {
                        'reward': reward,
                        'action': action,
                        'optimal': True
                    }

                return incentives
            else:
                print(f"Optimization status: {problem.status}")
                return self.dynamic_pricing(stations)

        except Exception as e:
            print(f"Optimization error: {e}")
            return self.dynamic_pricing(stations)

    def simulate_user_response(self, stations, incentives, num_users_per_station=100):
        """
        模拟用户响应

        参数:
            stations: List[Station]
            incentives: Dict of incentives
            num_users_per_station: 每个站点的潜在用户数

        返回:
            dict: Simulation results
        """
        total_participants = 0
        total_cost = 0
        bikes_rebalanced = 0

        station_results = {}

        for station in stations:
            incentive = incentives.get(station.id, {})
            reward = incentive.get('reward', 0)
            action = incentive.get('action', 'none')

            if action == 'none' or reward == 0:
                station_results[station.id] = {
                    'participants': 0,
                    'cost': 0,
                    'rebalanced': 0
                }
                continue

            # 估计平均绕行时间（简化）
            avg_detour = 5  # 分钟

            # 计算参与人数
            participants = self.user_model.expected_participants(
                num_users_per_station, reward, avg_detour
            )

            # 成本
            cost = participants * reward

            # 再平衡效果（简化：假设每个参与者移动1辆车）
            rebalanced = participants

            total_participants += participants
            total_cost += cost
            bikes_rebalanced += rebalanced

            station_results[station.id] = {
                'participants': participants,
                'cost': cost,
                'rebalanced': rebalanced
            }

        # 计算节省
        rebalancing_saved = bikes_rebalanced * self.rebalancing_cost
        net_savings = rebalancing_saved - total_cost
        roi = rebalancing_saved / total_cost if total_cost > 0 else 0

        return {
            'total_participants': total_participants,
            'total_cost': total_cost,
            'bikes_rebalanced': bikes_rebalanced,
            'rebalancing_saved': rebalancing_saved,
            'net_savings': net_savings,
            'roi': roi,
            'station_results': station_results
        }

    def optimize(self, stations, expected_users=None):
        """
        执行激励优化

        参数:
            stations: List[Station]
            expected_users: Optional dict of expected users per station

        返回:
            tuple: (incentives, simulation_results)
        """
        print(f"\n激励优化（策略: {self.strategy}）...")

        # 根据策略选择方法
        if self.strategy == 'static':
            incentives = self.static_pricing(stations)
        elif self.strategy == 'dynamic':
            incentives = self.dynamic_pricing(stations)
        elif self.strategy == 'optimization':
            incentives = self.optimize_with_cvxpy(stations, expected_users)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")

        # 模拟用户响应
        simulation = self.simulate_user_response(stations, incentives)

        # 打印摘要
        print(f"\n优化结果:")
        print(f"  激励站点数: {sum(1 for i in incentives.values() if i['reward'] > 0)}")
        print(f"  预期参与人数: {simulation['total_participants']:.0f}")
        print(f"  激励成本: ${simulation['total_cost']:.2f}")
        print(f"  节省成本: ${simulation['rebalancing_saved']:.2f}")
        print(f"  净收益: ${simulation['net_savings']:.2f}")
        print(f"  ROI: {simulation['roi']:.2f}x")

        return incentives, simulation


def demo():
    """演示激励优化"""
    print("=" * 70)
    print("Citi Bike 激励优化演示")
    print("=" * 70)

    # 创建模拟站点
    stations = [
        Station('downtown', capacity=100, current_bikes=15, net_flow_forecast=-10),
        Station('suburb', capacity=100, current_bikes=85, net_flow_forecast=5),
        Station('midtown', capacity=100, current_bikes=50, net_flow_forecast=0),
        Station('office_area', capacity=80, current_bikes=70, net_flow_forecast=8),
        Station('residential', capacity=120, current_bikes=20, net_flow_forecast=-15),
    ]

    print("\n站点状态:")
    print("-" * 70)
    for s in stations:
        status = "缺车" if s.is_deficit() else ("满车" if s.is_surplus() else "正常")
        print(f"  {s.id:20s}: {s.current_bikes:3d}/{s.capacity:3d} "
              f"({s.utilization*100:3.0f}%) - {status}")

    # 创建优化器
    optimizer = IncentiveOptimizer()

    # 静态定价
    print("\n" + "=" * 70)
    print("1. 静态定价策略")
    print("=" * 70)

    optimizer.strategy = 'static'
    static_incentives, static_sim = optimizer.optimize(stations)

    print("\n奖励方案:")
    for station_id, incentive in static_incentives.items():
        if incentive['reward'] > 0:
            print(f"  {station_id:20s}: ${incentive['reward']:.2f} ({incentive['action']})")

    # 动态定价
    print("\n" + "=" * 70)
    print("2. 动态定价策略")
    print("=" * 70)

    optimizer.strategy = 'dynamic'
    dynamic_incentives, dynamic_sim = optimizer.optimize(stations)

    print("\n奖励方案:")
    for station_id, incentive in dynamic_incentives.items():
        if incentive['reward'] > 0:
            print(f"  {station_id:20s}: ${incentive['reward']:.2f} "
                  f"(imbalance: {incentive['imbalance_score']:.2f})")

    # 对比
    print("\n" + "=" * 70)
    print("策略对比")
    print("=" * 70)

    comparison = pd.DataFrame({
        '静态定价': {
            'ROI': static_sim['roi'],
            '成本': static_sim['total_cost'],
            '节省': static_sim['net_savings'],
            '参与人数': static_sim['total_participants']
        },
        '动态定价': {
            'ROI': dynamic_sim['roi'],
            '成本': dynamic_sim['total_cost'],
            '节省': dynamic_sim['net_savings'],
            '参与人数': dynamic_sim['total_participants']
        }
    }).T

    print(comparison.to_string())

    print("\n" + "=" * 70)
    print("✓ 演示完成")
    print("=" * 70)


if __name__ == '__main__':
    demo()
