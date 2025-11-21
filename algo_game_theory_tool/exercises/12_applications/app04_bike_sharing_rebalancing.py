"""
练习 23: 共享单车再平衡激励机制 (Bike Sharing Rebalancing Incentives)

共享单车系统面临的核心运营挑战：供需不平衡
- 高峰期某些站点无车可借
- 某些站点停满无处还车
- 传统解决方案：雇佣卡车重新分配（成本高）

博弈论解决方案：设计激励机制，让用户帮助再平衡
- 用户还车到缺车站点获得奖励
- 用户从满车站点借车获得奖励

机制设计挑战：
1. 激励兼容：奖励必须足够吸引用户改变行为
2. 预算平衡：总奖励不能超过运营节省
3. 个体理性：用户参与激励系统比不参与更好
4. 真实性：用户报告真实的出行需求

应用案例：
- Mobike (摩拜): 红包车激励系统
- Ofo (小黄车): 信用分奖励系统
- Citi Bike (纽约): Bike Angels 奖励计划

任务：设计并实现共享单车再平衡的激励机制。
"""

from typing import List, Dict, Tuple, Optional


class Station:
    """单车站点"""

    def __init__(self, station_id: str, capacity: int, current_bikes: int,
                 demand_rate: float):
        """
        初始化站点

        参数:
            station_id: 站点ID
            capacity: 最大容量
            current_bikes: 当前单车数
            demand_rate: 需求率（借车 - 还车）
        """
        self.id = station_id
        self.capacity = capacity
        self.current_bikes = current_bikes
        self.demand_rate = demand_rate

    @property
    def available_bikes(self) -> int:
        """可借单车数"""
        return self.current_bikes

    @property
    def available_docks(self) -> int:
        """可停车位数"""
        return self.capacity - self.current_bikes

    @property
    def utilization(self) -> float:
        """利用率"""
        return self.current_bikes / self.capacity if self.capacity > 0 else 0

    def is_deficit(self) -> bool:
        """是否缺车（利用率低）"""
        return self.utilization < 0.2

    def is_surplus(self) -> bool:
        """是否满车（利用率高）"""
        return self.utilization > 0.8


class User:
    """用户"""

    def __init__(self, user_id: str, origin: str, destination: str,
                 time_value: float):
        """
        初始化用户

        参数:
            user_id: 用户ID
            origin: 起点站点
            destination: 终点站点
            time_value: 时间价值（愿意为节省1分钟支付的金额）
        """
        self.id = user_id
        self.origin = origin
        self.destination = destination
        self.time_value = time_value


class RebalancingMechanism:
    """再平衡激励机制"""

    def __init__(self, stations: List[Station], rebalancing_cost: float):
        """
        初始化激励机制

        参数:
            stations: 站点列表
            rebalancing_cost: 人工再平衡每辆车的成本
        """
        self.stations = {s.id: s for s in stations}
        self.rebalancing_cost = rebalancing_cost
        self.total_rewards_paid = 0.0

    def calculate_incentive(self, user: User) -> float:
        """
        计算用户应得的激励金额

        激励设计原则：
        1. 从满车站借车：缓解拥堵，给予奖励
        2. 还车到缺车站：补充供给，给予奖励
        3. 奖励应与站点不平衡程度相关
        4. 奖励不应超过人工再平衡的成本

        参数:
            user: 用户对象

        返回:
            float: 激励金额（正数为奖励，负数为罚款）
        """
        # TODO: 实现激励计算
        # 考虑：
        # 1. 起点站点状态（surplus/deficit/normal）
        # 2. 终点站点状态
        # 3. 基准奖励不超过 rebalancing_cost
        pass

    def is_incentive_compatible(self, user: User, alternative_destination: str,
                               detour_time: float) -> bool:
        """
        检查激励兼容性

        用户是否愿意为了奖励而绕路到替代站点？

        参数:
            user: 用户
            alternative_destination: 替代终点站
            detour_time: 绕路额外时间（分钟）

        返回:
            bool: 是否激励兼容
        """
        # TODO: 检查激励兼容性
        # 原目的地激励
        original_incentive = self.calculate_incentive(user)

        # 替代目的地激励
        # alternative_user = User(user.id, user.origin, alternative_destination, user.time_value)
        # alternative_incentive = self.calculate_incentive(alternative_user)

        # 绕路成本 = 时间价值 × 绕路时间
        # detour_cost = user.time_value * detour_time

        # 激励兼容: alternative_incentive - detour_cost > original_incentive
        pass


def design_static_pricing(stations: List[Station],
                         rebalancing_cost: float) -> Dict[str, float]:
    """
    设计静态定价策略

    简单策略：根据站点状态给予固定奖励

    参数:
        stations: 站点列表
        rebalancing_cost: 再平衡成本

    返回:
        dict: {station_id: reward}（正为借车奖励，负为还车奖励）
    """
    # TODO: 实现静态定价
    # 缺车站：还车奖励为正
    # 满车站：借车奖励为正
    pass


def design_dynamic_pricing(stations: List[Station],
                          demand_forecast: Dict[str, float],
                          rebalancing_cost: float) -> Dict[str, float]:
    """
    设计动态定价策略

    根据需求预测动态调整奖励

    参数:
        stations: 站点列表
        demand_forecast: 未来需求预测 {station_id: net_demand}
        rebalancing_cost: 再平衡成本

    返回:
        dict: {station_id: reward}
    """
    # TODO: 实现动态定价
    # 考虑：
    # 1. 当前状态
    # 2. 未来需求趋势
    # 3. 提前激励用户
    pass


def simulate_user_response(mechanism: RebalancingMechanism,
                          users: List[User],
                          alternative_stations: Dict[str, List[Tuple[str, float]]]) -> Dict:
    """
    模拟用户对激励的响应

    参数:
        mechanism: 激励机制
        users: 用户列表
        alternative_stations: 替代站点 {destination: [(alt_station, detour_time), ...]}

    返回:
        dict: 模拟结果（原始选择数、改变选择数、总节省成本）
    """
    # TODO: 模拟用户响应
    # 对每个用户：
    # 1. 计算原目的地激励
    # 2. 检查是否有更好的替代站点
    # 3. 如果激励兼容，用户改变选择
    pass


def evaluate_mechanism(mechanism: RebalancingMechanism,
                      users: List[User]) -> Dict[str, float]:
    """
    评估机制性能

    返回:
        dict: {
            'total_rewards': 总奖励支出,
            'participation_rate': 参与率,
            'rebalancing_effectiveness': 再平衡效果,
            'cost_savings': 节省的人工成本
        }
    """
    # TODO: 实现机制评估
    pass


# HINT: 激励应与站点不平衡程度成正比
# HINT: 借车和还车是对称的：从A借到B = 从B还到A
# HINT: 动态定价可以提前应对高峰需求
# HINT: 用户响应取决于 reward - detour_cost


def test():
    """测试函数"""
    from exercise_runner import Color

    print(f"{Color.CYAN}测试 1: 站点状态识别{Color.END}")

    stations = [
        Station('downtown', capacity=100, current_bikes=15, demand_rate=-5),  # 缺车
        Station('suburb', capacity=100, current_bikes=85, demand_rate=3),      # 满车
        Station('midtown', capacity=100, current_bikes=50, demand_rate=0)      # 正常
    ]

    print(f"  站点状态:")
    for s in stations:
        status = "缺车" if s.is_deficit() else ("满车" if s.is_surplus() else "正常")
        print(f"    {s.id}: {s.current_bikes}/{s.capacity} ({s.utilization*100:.0f}%) - {status}")

    if stations[0].is_deficit() and stations[1].is_surplus():
        print(f"  {Color.GREEN}✓{Color.END} 站点状态识别正确")
    else:
        print(f"  {Color.RED}✗{Color.END} 站点状态识别错误")
        return False

    print(f"\n{Color.CYAN}测试 2: 激励计算{Color.END}")

    mechanism = RebalancingMechanism(stations, rebalancing_cost=5.0)

    # 场景1: 从满车站借到缺车站（帮助再平衡）
    user1 = User('u1', origin='suburb', destination='downtown', time_value=2.0)

    # 场景2: 从缺车站借到满车站（加剧不平衡）
    user2 = User('u2', origin='downtown', destination='suburb', time_value=2.0)

    # 场景3: 正常站点之间
    user3 = User('u3', origin='midtown', destination='midtown', time_value=2.0)

    try:
        incentive1 = mechanism.calculate_incentive(user1)
        incentive2 = mechanism.calculate_incentive(user2)
        incentive3 = mechanism.calculate_incentive(user3)

        print(f"  用户1 (满车站→缺车站): ${incentive1:.2f}")
        print(f"  用户2 (缺车站→满车站): ${incentive2:.2f}")
        print(f"  用户3 (正常站之间): ${incentive3:.2f}")

        if incentive1 > 0 and incentive2 < 0:
            print(f"  {Color.GREEN}✓{Color.END} 激励方向正确")
        else:
            print(f"  {Color.YELLOW}提示：完成 calculate_incentive 实现{Color.END}")
    except:
        print(f"  {Color.YELLOW}提示：完成 calculate_incentive 实现{Color.END}")

    print(f"\n{Color.CYAN}测试 3: 激励兼容性{Color.END}")

    print(f"  {Color.YELLOW}场景：{Color.END}")
    print(f"    用户想从 suburb 到 downtown")
    print(f"    替代方案：到 midtown（需绕路5分钟）")
    print(f"    用户时间价值：$2/分钟")
    print(f"    绕路成本：5 × $2 = $10")

    print(f"  ")
    print(f"    如果 midtown 的奖励 > downtown 的奖励 + $10")
    print(f"    则用户会选择绕路到 midtown")
    print(f"    {Color.GREEN}这就是激励兼容！{Color.END}")

    print(f"\n{Color.CYAN}测试 4: 静态定价策略{Color.END}")

    try:
        pricing = design_static_pricing(stations, rebalancing_cost=5.0)

        if pricing:
            print(f"  {Color.YELLOW}静态定价：{Color.END}")
            for station_id, reward in pricing.items():
                print(f"    {station_id}: ${reward:.2f}")
            print(f"  {Color.GREEN}✓{Color.END} 静态定价完成")
        else:
            print(f"  {Color.YELLOW}提示：完成 design_static_pricing 实现{Color.END}")
    except:
        print(f"  {Color.YELLOW}提示：完成 design_static_pricing 实现{Color.END}")

    print(f"\n{Color.CYAN}测试 5: 真实案例 - Citi Bike Angels{Color.END}")

    print(f"  {Color.YELLOW}Citi Bike (纽约) 的 Bike Angels 计划：{Color.END}")
    print(f"    - 用户通过帮助再平衡获得积分")
    print(f"    - 积分可兑换免费骑行、会员资格")
    print(f"    - 每天节省数千美元的卡车调度成本")
    print(f"  ")
    print(f"    奖励规则：")
    print(f"      - 还车到缺车站：2-4 积分")
    print(f"      - 从满车站借车：2-4 积分")
    print(f"      - 积分根据站点不平衡程度动态调整")
    print(f"  ")
    print(f"    成果：")
    print(f"      - 20% 的用户参与 Bike Angels 计划")
    print(f"      - 减少 30% 的人工再平衡需求")
    print(f"      - 每年节省 $500K+ 运营成本")

    print(f"\n{Color.CYAN}测试 6: 真实案例 - 摩拜单车红包车{Color.END}")

    print(f"  {Color.YELLOW}摩拜单车（中国）的红包车激励：{Color.END}")
    print(f"    - 特定单车标记为\"红包车\"")
    print(f"    - 骑行并还到指定区域获得现金奖励")
    print(f"    - 奖励金额：¥0.5 - ¥10 不等")
    print(f"  ")
    print(f"    设计巧妙之处：")
    print(f"      - 游戏化：用户\"寻宝\"心态")
    print(f"      - 动态调整：高峰期增加奖励")
    print(f"      - 精准定位：只激励需要的调度方向")
    print(f"  ")
    print(f"    挑战：")
    print(f"      - 羊毛党：专门薅羊毛的用户")
    print(f"      - 作弊：多账号、虚假骑行")
    print(f"      - {Color.RED}机制设计需要考虑防作弊！{Color.END}")

    print(f"\n{Color.CYAN}测试 7: 机制设计原则{Color.END}")

    print(f"  {Color.YELLOW}1. 激励兼容 (Incentive Compatible):{Color.END}")
    print(f"     奖励必须让用户真实响应")
    print(f"     reward - detour_cost > 0")
    print(f"  ")
    print(f"  {Color.YELLOW}2. 预算平衡 (Budget Balanced):{Color.END}")
    print(f"     总奖励 ≤ 节省的人工成本")
    print(f"     Σ rewards ≤ rebalancing_cost × bikes_rebalanced")
    print(f"  ")
    print(f"  {Color.YELLOW}3. 个体理性 (Individual Rational):{Color.END}")
    print(f"     参与机制 ≥ 不参与")
    print(f"     utility_with_mechanism ≥ utility_without")
    print(f"  ")
    print(f"  {Color.YELLOW}4. 真实性 (Truthfulness):{Color.END}")
    print(f"     用户报告真实需求最优")
    print(f"     防止虚假骑行、多账号作弊")

    print(f"\n{Color.CYAN}测试 8: 高级话题{Color.END}")

    print(f"  {Color.YELLOW}动态定价 vs 静态定价：{Color.END}")
    print(f"    静态：简单，但无法应对需求波动")
    print(f"    动态：复杂，但效果更好")
    print(f"  ")
    print(f"  {Color.YELLOW}需求预测的作用：{Color.END}")
    print(f"    早高峰前：激励还车到商业区")
    print(f"    晚高峰前：激励还车到住宅区")
    print(f"    {Color.GREEN}提前应对，而不是被动响应{Color.END}")
    print(f"  ")
    print(f"  {Color.YELLOW}多目标优化：{Color.END}")
    print(f"    - 最小化运营成本")
    print(f"    - 最大化用户满意度")
    print(f"    - 保持系统可用性")
    print(f"    {Color.RED}需要权衡！{Color.END}")

    print(f"\n{Color.YELLOW}💡 共享单车再平衡的启示：{Color.END}")
    print(f"{Color.YELLOW}   - 激励设计可以改变用户行为{Color.END}")
    print(f"{Color.YELLOW}   - 众包解决方案比中心化调度更高效{Color.END}")
    print(f"{Color.YELLOW}   - 机制设计需要考虑现实约束（预算、作弊）{Color.END}")
    print(f"{Color.YELLOW}   - 应用：共享汽车、共享充电宝、云计算负载均衡{Color.END}")

    return True


if __name__ == '__main__':
    test()
