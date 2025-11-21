"""
练习 22: 网络成本分摊 (Network Cost Sharing)

成本分摊是博弈论在实践中的重要应用。如何公平地分摊共享资源的成本？

应用场景：
1. **拼车费用**: 3个人拼车，如何分摊车费？
2. **网络基础设施**: 多个ISP共享网络设备，如何分摊成本？
3. **机场跑道**: 不同大小的飞机使用跑道，如何分摊建设成本？
4. **云计算资源**: 多个用户共享服务器，如何分摊成本？

核心问题：
给定一组用户和他们使用的资源，如何公平地分配总成本？

公平性标准：
1. **效率**: Σ x_i = 总成本（完全分摊）
2. **个体理性**: x_i ≤ 用户i单独承担的成本
3. **无补贴**: 任何联盟的分摊 ≤ 该联盟单独的成本
4. **对称性**: 贡献相同的用户分摊相同

Shapley值提供了唯一满足这些公理的分摊方案！

任务：实现各种成本分摊方法，包括Shapley值、平均分摊、边际成本等。
"""

from typing import List, Dict, Tuple, Callable
from itertools import combinations


class User:
    """用户"""

    def __init__(self, user_id: str, usage: float, value: float):
        """
        初始化用户

        参数:
            user_id: 用户ID
            usage: 资源使用量
            value: 对服务的估值
        """
        self.id = user_id
        self.usage = usage
        self.value = value


class CostSharingProblem:
    """成本分摊问题"""

    def __init__(self, users: List[User], cost_function: Callable):
        """
        初始化成本分摊问题

        参数:
            users: 用户列表
            cost_function: 成本函数 C(S)，输入用户集合，输出总成本
        """
        self.users = {u.id: u for u in users}
        self.cost_function = cost_function

    def shapley_cost_sharing(self) -> Dict[str, float]:
        """
        使用Shapley值进行成本分摊

        Shapley值的成本分摊解释：
        每个用户支付其"平均边际成本"

        返回:
            dict: {user_id: cost_share}
        """
        # TODO: 实现Shapley值成本分摊
        # 使用之前练习中的shapley_value函数
        pass

    def equal_sharing(self) -> Dict[str, float]:
        """
        平均分摊：每个用户支付相同金额

        这是最简单的方法，但可能不公平

        返回:
            dict: {user_id: cost_share}
        """
        # TODO: 实现平均分摊
        # 总成本 / 用户数
        pass

    def proportional_sharing(self) -> Dict[str, float]:
        """
        比例分摊：根据使用量比例分摊

        用户i的分摊 = (用户i的使用量 / 总使用量) × 总成本

        返回:
            dict: {user_id: cost_share}
        """
        # TODO: 实现比例分摊
        pass

    def marginal_cost_sharing(self) -> Dict[str, float]:
        """
        边际成本分摊：每个用户支付其边际成本

        边际成本 = C(所有用户) - C(除了该用户)

        注意：边际成本之和可能不等于总成本！

        返回:
            dict: {user_id: marginal_cost}
        """
        # TODO: 实现边际成本分摊
        pass

    def nucleolus_cost_sharing(self) -> Dict[str, float]:
        """
        Nucleolus分摊（高级！）

        Nucleolus是协同博弈的另一个解概念：
        最小化最大的"不满"(excess)

        返回:
            dict: {user_id: cost_share}
        """
        # TODO: 实现nucleolus（可选，很难！）
        pass

    def check_budget_balance(self, sharing: Dict[str, float]) -> bool:
        """
        检查预算平衡：分摊总和是否等于总成本

        参数:
            sharing: 分摊方案

        返回:
            bool: 是否预算平衡
        """
        # TODO: 检查 Σ sharing = C(所有用户)
        pass

    def check_individual_rationality(self, sharing: Dict[str, float]) -> bool:
        """
        检查个体理性：每个用户的分摊是否不超过其单独承担的成本

        参数:
            sharing: 分摊方案

        返回:
            bool: 是否满足个体理性
        """
        # TODO: 检查 sharing[i] ≤ C({i}) for all i
        pass

    def check_core_membership(self, sharing: Dict[str, float]) -> Tuple[bool, List]:
        """
        检查分摊方案是否在核心中

        在核心中 ⟺ 没有联盟有动机脱离

        参数:
            sharing: 分摊方案

        返回:
            tuple: (in_core, blocking_coalitions)
        """
        # TODO: 检查核心条件
        # 对所有联盟S: Σ_{i∈S} sharing[i] ≤ C(S)
        pass


# HINT: Shapley值 = 平均边际成本贡献
# HINT: 边际成本之和通常不等于总成本
# HINT: Shapley值保证在核心中（对凸成本函数）
# HINT: 机场问题是经典的成本分摊案例


def test():
    """测试函数"""
    from exercise_runner import Color

    print(f"{Color.CYAN}测试 1: 拼车成本分摊{Color.END}")

    # 3个人拼车，成本函数
    # C(S) = 如果|S|=0则0，如果|S|>0则10（固定成本）+ 2×|S|（可变成本）
    def ride_sharing_cost(user_set):
        if not user_set:
            return 0
        return 10 + 2 * len(user_set)  # 固定成本 + 每人边际成本

    users = [
        User('Alice', usage=1, value=20),
        User('Bob', usage=1, value=18),
        User('Carol', usage=1, value=15)
    ]

    problem = CostSharingProblem(users, ride_sharing_cost)

    print(f"  {Color.YELLOW}场景: 3人拼车{Color.END}")
    print(f"    总成本: ${ride_sharing_cost({'Alice', 'Bob', 'Carol'})}")

    print(f"\n{Color.CYAN}测试 2: 不同分摊方法{Color.END}")

    # 平均分摊
    equal = problem.equal_sharing()
    if equal:
        print(f"  {Color.GREEN}✓{Color.END} 平均分摊:")
        for user_id, cost in equal.items():
            print(f"    {user_id}: ${cost:.2f}")

    # 比例分摊（这里usage相同，结果同平均）
    prop = problem.proportional_sharing()
    if prop:
        print(f"\n  {Color.GREEN}✓{Color.END} 比例分摊:")
        for user_id, cost in prop.items():
            print(f"    {user_id}: ${cost:.2f}")

    # Shapley值
    shapley = problem.shapley_cost_sharing()
    if shapley:
        print(f"\n  {Color.GREEN}✓{Color.END} Shapley值分摊:")
        for user_id, cost in shapley.items():
            print(f"    {user_id}: ${cost:.2f}")

    print(f"\n{Color.CYAN}测试 3: 机场问题（经典案例）{Color.END}")

    # 机场跑道成本分摊
    # 小飞机需要1000米跑道，大飞机需要2000米跑道
    # 建1000米跑道成本$100万，建2000米跑道成本$150万

    def airport_cost(user_set):
        """机场成本函数"""
        if not user_set:
            return 0
        if 'large' in user_set:
            return 150  # 需要2000米跑道
        else:
            return 100  # 只需1000米跑道

    users_airport = [
        User('small', usage=1000, value=80),
        User('large', usage=2000, value=120)
    ]

    problem_airport = CostSharingProblem(users_airport, airport_cost)

    print(f"  {Color.YELLOW}场景: 机场跑道成本分摊{Color.END}")
    print(f"    小飞机需要: 1000米跑道")
    print(f"    大飞机需要: 2000米跑道")
    print(f"    1000米成本: $100万")
    print(f"    2000米成本: $150万")

    # 不同方法
    shapley_airport = problem_airport.shapley_cost_sharing()
    if shapley_airport:
        print(f"\n  {Color.GREEN}Shapley值分摊：{Color.END}")
        for user_id, cost in shapley_airport.items():
            print(f"    {user_id}: ${cost:.0f}万")

        print(f"\n  {Color.YELLOW}分析：{Color.END}")
        print(f"    小飞机分摊: ${shapley_airport.get('small', 0):.0f}万")
        print(f"    大飞机分摊: ${shapley_airport.get('large', 0):.0f}万")
        print(f"    ")
        print(f"    逻辑:")
        print(f"      - 1000米部分由两者平分: 各$50万")
        print(f"      - 额外500米只有大飞机用: $50万")
        print(f"      - 所以: 小=$50万, 大=$100万")

    print(f"\n{Color.CYAN}测试 4: 公平性检查{Color.END}")

    if shapley_airport:
        is_balanced = problem_airport.check_budget_balance(shapley_airport)
        is_rational = problem_airport.check_individual_rationality(shapley_airport)
        is_core, blocking = problem_airport.check_core_membership(shapley_airport)

        print(f"  预算平衡: {Color.GREEN if is_balanced else Color.RED}{is_balanced}{Color.END}")
        print(f"  个体理性: {Color.GREEN if is_rational else Color.RED}{is_rational}{Color.END}")
        print(f"  在核心中: {Color.GREEN if is_core else Color.RED}{is_core}{Color.END}")

    print(f"\n{Color.CYAN}测试 5: 实际应用{Color.END}")

    print(f"  {Color.YELLOW}成本分摊的真实应用：{Color.END}")
    print(f"    ")
    print(f"    1. 电信网络:")
    print(f"       - AT&T, Verizon等共享光纤")
    print(f"       - Shapley值分摊基础设施成本")
    print(f"    ")
    print(f"    2. 机场运营:")
    print(f"       - 不同航空公司共享跑道")
    print(f"       - 根据飞机大小分摊成本")
    print(f"    ")
    print(f"    3. 云计算:")
    print(f"       - AWS, Azure等按使用量计费")
    print(f"       - 固定成本+可变成本分摊")
    print(f"    ")
    print(f"    4. 共享办公:")
    print(f"       - WeWork等共享空间")
    print(f"       - 公共设施成本分摊")

    print(f"\n{Color.CYAN}测试 6: 不同方法比较{Color.END}")

    comparison = """
    分摊方法对比：

    | 方法         | 预算平衡 | 个体理性 | 在核心中 | 公平性 | 计算复杂度 |
    |--------------|----------|----------|----------|--------|------------|
    | 平均分摊     | ✓        | ✗        | ✗        | 低     | O(1)       |
    | 比例分摊     | ✓        | ?        | ?        | 中     | O(n)       |
    | 边际成本     | ✗        | ✓        | ?        | ?      | O(n)       |
    | Shapley值    | ✓        | ✓*       | ✓*       | ✓      | O(2^n)     |
    | Nucleolus    | ✓        | ✓        | ✓        | ✓      | NP-hard    |

    *对于凸成本函数
    """

    print(comparison)

    print(f"\n{Color.YELLOW}💡 成本分摊的启示：{Color.END}")
    print(f"{Color.YELLOW}   - Shapley值提供公理化的公平分摊{Color.END}")
    print(f"{Color.YELLOW}   - 实践中常用简化方法（计算复杂度）{Color.END}")
    print(f"{Color.YELLOW}   - 需要平衡公平性和效率{Color.END}")
    print(f"{Color.YELLOW}   - 广泛应用于网络、交通、云计算等领域{Color.END}")

    return True


if __name__ == '__main__':
    test()
