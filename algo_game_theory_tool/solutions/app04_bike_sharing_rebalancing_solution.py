"""
练习 23 参考答案: 共享单车再平衡激励机制

这是app04_bike_sharing_rebalancing.py的完整参考实现。
"""

from typing import List, Dict, Tuple, Optional


class Station:
    """单车站点"""

    def __init__(self, station_id: str, capacity: int, current_bikes: int,
                 demand_rate: float):
        self.id = station_id
        self.capacity = capacity
        self.current_bikes = current_bikes
        self.demand_rate = demand_rate

    @property
    def available_bikes(self) -> int:
        return self.current_bikes

    @property
    def available_docks(self) -> int:
        return self.capacity - self.current_bikes

    @property
    def utilization(self) -> float:
        return self.current_bikes / self.capacity if self.capacity > 0 else 0

    def is_deficit(self) -> bool:
        return self.utilization < 0.2

    def is_surplus(self) -> bool:
        return self.utilization > 0.8


class User:
    """用户"""

    def __init__(self, user_id: str, origin: str, destination: str,
                 time_value: float):
        self.id = user_id
        self.origin = origin
        self.destination = destination
        self.time_value = time_value


class RebalancingMechanism:
    """再平衡激励机制 - 完整实现"""

    def __init__(self, stations: List[Station], rebalancing_cost: float):
        self.stations = {s.id: s for s in stations}
        self.rebalancing_cost = rebalancing_cost
        self.total_rewards_paid = 0.0

    def calculate_incentive(self, user: User) -> float:
        """
        计算用户应得的激励金额 - 完整实现

        实现思路：
        1. 评估起点和终点站点的状态
        2. 帮助再平衡的行为给予奖励
        3. 加剧不平衡的行为给予惩罚（或不奖励）
        """
        origin_station = self.stations.get(user.origin)
        dest_station = self.stations.get(user.destination)

        if not origin_station or not dest_station:
            return 0.0

        incentive = 0.0

        # 从满车站借车：减少满车问题，给予奖励
        if origin_station.is_surplus():
            # 奖励与满车程度成正比
            surplus_degree = (origin_station.utilization - 0.8) / 0.2
            incentive += self.rebalancing_cost * 0.5 * surplus_degree

        # 从缺车站借车：加剧缺车问题，给予惩罚
        if origin_station.is_deficit():
            deficit_degree = (0.2 - origin_station.utilization) / 0.2
            incentive -= self.rebalancing_cost * 0.3 * deficit_degree

        # 还车到缺车站：补充供给，给予奖励
        if dest_station.is_deficit():
            deficit_degree = (0.2 - dest_station.utilization) / 0.2
            incentive += self.rebalancing_cost * 0.5 * deficit_degree

        # 还车到满车站：加剧满车问题，给予惩罚
        if dest_station.is_surplus():
            surplus_degree = (dest_station.utilization - 0.8) / 0.2
            incentive -= self.rebalancing_cost * 0.3 * surplus_degree

        return incentive

    def is_incentive_compatible(self, user: User, alternative_destination: str,
                               detour_time: float) -> bool:
        """
        检查激励兼容性 - 完整实现

        用户是否愿意为了奖励而绕路？
        """
        # 原目的地激励
        original_incentive = self.calculate_incentive(user)

        # 替代目的地激励
        alternative_user = User(user.id, user.origin, alternative_destination,
                              user.time_value)
        alternative_incentive = self.calculate_incentive(alternative_user)

        # 绕路成本
        detour_cost = user.time_value * detour_time

        # 激励兼容：额外奖励超过绕路成本
        return (alternative_incentive - original_incentive) > detour_cost


def design_static_pricing(stations: List[Station],
                         rebalancing_cost: float) -> Dict[str, float]:
    """
    设计静态定价策略 - 完整实现

    简单但有效的策略：根据站点状态给予固定奖励
    """
    pricing = {}

    for station in stations:
        if station.is_deficit():
            # 缺车站：还车奖励
            deficit_degree = (0.2 - station.utilization) / 0.2
            pricing[station.id] = rebalancing_cost * 0.5 * deficit_degree

        elif station.is_surplus():
            # 满车站：借车奖励（表示为负的还车奖励）
            surplus_degree = (station.utilization - 0.8) / 0.2
            pricing[station.id] = -rebalancing_cost * 0.5 * surplus_degree

        else:
            # 正常站点：无奖励
            pricing[station.id] = 0.0

    return pricing


def design_dynamic_pricing(stations: List[Station],
                          demand_forecast: Dict[str, float],
                          rebalancing_cost: float) -> Dict[str, float]:
    """
    设计动态定价策略 - 完整实现

    考虑未来需求，提前激励用户
    """
    pricing = {}

    for station in stations:
        current_util = station.utilization
        forecast_demand = demand_forecast.get(station.id, 0.0)

        # 预测未来利用率
        # 简化模型：future_bikes = current_bikes + forecast_demand
        future_bikes = max(0, min(station.capacity,
                                 station.current_bikes + forecast_demand))
        future_util = future_bikes / station.capacity

        # 综合当前和未来状态
        weight_current = 0.6
        weight_future = 0.4
        weighted_util = weight_current * current_util + weight_future * future_util

        # 根据加权利用率定价
        if weighted_util < 0.2:
            # 将会缺车：鼓励还车
            degree = (0.2 - weighted_util) / 0.2
            pricing[station.id] = rebalancing_cost * 0.7 * degree

        elif weighted_util > 0.8:
            # 将会满车：鼓励借车
            degree = (weighted_util - 0.8) / 0.2
            pricing[station.id] = -rebalancing_cost * 0.7 * degree

        else:
            pricing[station.id] = 0.0

    return pricing


def simulate_user_response(mechanism: RebalancingMechanism,
                          users: List[User],
                          alternative_stations: Dict[str, List[Tuple[str, float]]]) -> Dict:
    """
    模拟用户对激励的响应 - 完整实现
    """
    original_choices = 0
    changed_choices = 0
    total_cost_savings = 0.0

    for user in users:
        original_incentive = mechanism.calculate_incentive(user)
        original_choices += 1

        best_alternative = None
        best_net_benefit = 0.0

        # 检查所有替代站点
        alternatives = alternative_stations.get(user.destination, [])

        for alt_station, detour_time in alternatives:
            alt_user = User(user.id, user.origin, alt_station, user.time_value)
            alt_incentive = mechanism.calculate_incentive(alt_user)

            detour_cost = user.time_value * detour_time
            net_benefit = (alt_incentive - original_incentive) - detour_cost

            if net_benefit > best_net_benefit:
                best_net_benefit = net_benefit
                best_alternative = alt_station

        # 如果有更好的替代方案，用户改变选择
        if best_alternative is not None and best_net_benefit > 0:
            changed_choices += 1
            # 假设改变选择相当于节省一次人工再平衡
            total_cost_savings += mechanism.rebalancing_cost

    return {
        'original_choices': original_choices,
        'changed_choices': changed_choices,
        'participation_rate': changed_choices / original_choices if original_choices > 0 else 0,
        'total_cost_savings': total_cost_savings
    }


def evaluate_mechanism(mechanism: RebalancingMechanism,
                      users: List[User]) -> Dict[str, float]:
    """
    评估机制性能 - 完整实现
    """
    total_rewards = 0.0
    positive_incentives = 0
    rebalancing_trips = 0

    for user in users:
        incentive = mechanism.calculate_incentive(user)
        total_rewards += abs(incentive)  # 总支出（包括正负激励）

        if incentive > 0:
            positive_incentives += 1

        # 如果用户从满车站到缺车站，或从缺车站到满车站，算作再平衡行程
        origin = mechanism.stations.get(user.origin)
        dest = mechanism.stations.get(user.destination)

        if origin and dest:
            if (origin.is_surplus() and dest.is_deficit()) or \
               (origin.is_deficit() and dest.is_surplus()):
                rebalancing_trips += 1

    participation_rate = positive_incentives / len(users) if users else 0
    rebalancing_effectiveness = rebalancing_trips / len(users) if users else 0
    cost_savings = rebalancing_trips * mechanism.rebalancing_cost - total_rewards

    return {
        'total_rewards': total_rewards,
        'participation_rate': participation_rate,
        'rebalancing_effectiveness': rebalancing_effectiveness,
        'cost_savings': cost_savings
    }


def demonstrate_citi_bike_angels():
    """演示 Citi Bike Angels 真实案例"""
    print("=" * 70)
    print("Citi Bike Angels 案例研究")
    print("=" * 70)

    # 模拟纽约曼哈顿的几个站点
    stations = [
        Station('grand_central', capacity=60, current_bikes=5, demand_rate=-8),   # 早高峰缺车
        Station('residential_area', capacity=40, current_bikes=35, demand_rate=6), # 住宅区满车
        Station('midtown', capacity=50, current_bikes=25, demand_rate=0),
    ]

    print("\n站点状态（早高峰）：")
    print("-" * 70)
    for s in stations:
        status = "缺车" if s.is_deficit() else ("满车" if s.is_surplus() else "正常")
        print(f"  {s.id:20s}: {s.current_bikes:2d}/{s.capacity:2d} ({s.utilization*100:3.0f}%) - {status}")

    mechanism = RebalancingMechanism(stations, rebalancing_cost=5.0)

    print("\n激励策略：")
    print("-" * 70)

    # 典型用户行程
    trips = [
        User('u1', 'residential_area', 'grand_central', time_value=3.0),  # 通勤
        User('u2', 'grand_central', 'midtown', time_value=2.5),
        User('u3', 'residential_area', 'midtown', time_value=2.0),
    ]

    for trip in trips:
        incentive = mechanism.calculate_incentive(trip)
        points = int(abs(incentive) * 2)  # 转换为积分
        direction = "奖励" if incentive > 0 else "惩罚"

        print(f"  {trip.origin:20s} → {trip.destination:20s}: "
              f"{direction} {points} 积分 (${abs(incentive):.2f})")

    print("\n成果：")
    print("-" * 70)
    print("  - 每天约 1000 名活跃 Angels")
    print("  - 每天完成约 3000 次激励行程")
    print("  - 减少 30% 的卡车调度需求")
    print("  - 年度节省：约 $500,000 运营成本")
    print("  - 用户满意度提升：减少 40% 的\"无车可借\"投诉")


def demonstrate_mobike_red_packet():
    """演示摩拜红包车案例"""
    print("\n" + "=" * 70)
    print("摩拜单车红包车案例")
    print("=" * 70)

    # 模拟中国城市高峰场景
    stations = [
        Station('subway_station', capacity=100, current_bikes=10, demand_rate=-15),
        Station('office_area', capacity=80, current_bikes=70, demand_rate=10),
        Station('residential', capacity=120, current_bikes=95, demand_rate=8),
    ]

    print("\n站点状态（早高峰 8:00）：")
    print("-" * 70)
    for s in stations:
        status = "缺车" if s.is_deficit() else ("满车" if s.is_surplus() else "正常")
        print(f"  {s.id:20s}: {s.current_bikes:3d}/{s.capacity:3d} "
              f"({s.utilization*100:3.0f}%) - {status}")

    # 静态定价
    static_pricing = design_static_pricing(stations, rebalancing_cost=3.0)

    print("\n红包车奖励（静态）：")
    print("-" * 70)
    for station_id, reward in static_pricing.items():
        if reward > 0:
            print(f"  还车到 {station_id:20s}: ¥{reward:.2f}")
        elif reward < 0:
            print(f"  从 {station_id:20s} 借车: ¥{abs(reward):.2f}")

    # 动态定价（考虑未来需求）
    demand_forecast = {
        'subway_station': -10,   # 继续流失
        'office_area': 5,        # 继续增加
        'residential': 3,        # 缓慢增加
    }

    dynamic_pricing = design_dynamic_pricing(stations, demand_forecast,
                                            rebalancing_cost=3.0)

    print("\n红包车奖励（动态，预测未来30分钟）：")
    print("-" * 70)
    for station_id, reward in dynamic_pricing.items():
        if reward > 0:
            print(f"  还车到 {station_id:20s}: ¥{reward:.2f}")
        elif reward < 0:
            print(f"  从 {station_id:20s} 借车: ¥{abs(reward):.2f}")

    print("\n关键洞察：")
    print("-" * 70)
    print("  - 动态定价提供更高的奖励（提前应对高峰）")
    print("  - 游戏化设计增加用户参与度")
    print("  - 需要防止羊毛党滥用系统")


if __name__ == '__main__':
    # 运行演示
    demonstrate_citi_bike_angels()
    demonstrate_mobike_red_packet()

    # 运行测试
    print("\n" + "=" * 70)
    print("运行单元测试")
    print("=" * 70)

    from app04_bike_sharing_rebalancing import test
    test()
