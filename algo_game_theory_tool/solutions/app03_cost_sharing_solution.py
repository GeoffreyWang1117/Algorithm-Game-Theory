"""
练习 22 参考答案: 网络成本分摊

这是app03_cost_sharing.py的完整参考实现。
"""

from typing import List, Dict, Tuple, Callable
from itertools import combinations, permutations


class User:
    """用户"""

    def __init__(self, user_id: str, usage: float, value: float):
        self.id = user_id
        self.usage = usage
        self.value = value


class CostSharingProblem:
    """成本分摊问题 - 完整实现"""

    def __init__(self, users: List[User], cost_function: Callable):
        self.users = {u.id: u for u in users}
        self.cost_function = cost_function

    def shapley_cost_sharing(self) -> Dict[str, float]:
        """
        使用Shapley值进行成本分摊 - 完整实现

        实现思路：
        1. 枚举所有用户到达顺序的排列
        2. 对每个排列，计算每个用户的边际成本贡献
        3. 平均所有排列中的边际成本
        """
        user_ids = list(self.users.keys())
        n = len(user_ids)

        shapley_values = {u_id: 0.0 for u_id in user_ids}

        # 枚举所有排列
        for perm in permutations(user_ids):
            # 对这个排列，计算每个用户的边际成本
            coalition = set()

            for user_id in perm:
                # 用户加入前的成本
                cost_before = self.cost_function(coalition)

                # 用户加入
                coalition.add(user_id)

                # 用户加入后的成本
                cost_after = self.cost_function(coalition)

                # 边际成本贡献
                marginal_cost = cost_after - cost_before

                shapley_values[user_id] += marginal_cost

        # 平均
        num_permutations = 1
        for i in range(1, n + 1):
            num_permutations *= i

        for user_id in shapley_values:
            shapley_values[user_id] /= num_permutations

        return shapley_values

    def equal_sharing(self) -> Dict[str, float]:
        """平均分摊 - 完整实现"""
        total_cost = self.cost_function(set(self.users.keys()))
        n_users = len(self.users)

        if n_users == 0:
            return {}

        equal_share = total_cost / n_users

        return {u_id: equal_share for u_id in self.users}

    def proportional_sharing(self) -> Dict[str, float]:
        """比例分摊 - 完整实现"""
        total_cost = self.cost_function(set(self.users.keys()))
        total_usage = sum(u.usage for u in self.users.values())

        if total_usage == 0:
            return self.equal_sharing()

        sharing = {}
        for user_id, user in self.users.items():
            sharing[user_id] = (user.usage / total_usage) * total_cost

        return sharing

    def marginal_cost_sharing(self) -> Dict[str, float]:
        """边际成本分摊 - 完整实现"""
        all_users = set(self.users.keys())
        cost_all = self.cost_function(all_users)

        sharing = {}
        for user_id in self.users:
            # 除了该用户的所有其他用户
            others = all_users - {user_id}
            cost_others = self.cost_function(others)

            # 边际成本
            marginal_cost = cost_all - cost_others
            sharing[user_id] = marginal_cost

        return sharing

    def check_budget_balance(self, sharing: Dict[str, float]) -> bool:
        """检查预算平衡 - 完整实现"""
        total_sharing = sum(sharing.values())
        total_cost = self.cost_function(set(self.users.keys()))

        # 允许小的浮点误差
        return abs(total_sharing - total_cost) < 0.01

    def check_individual_rationality(self, sharing: Dict[str, float]) -> bool:
        """检查个体理性 - 完整实现"""
        for user_id, cost_share in sharing.items():
            # 用户单独的成本
            standalone_cost = self.cost_function({user_id})

            if cost_share > standalone_cost + 0.01:  # 允许小误差
                return False

        return True

    def check_core_membership(self, sharing: Dict[str, float]) -> Tuple[bool, List]:
        """检查核心成员 - 完整实现"""
        blocking_coalitions = []
        user_ids = list(self.users.keys())

        # 检查所有可能的联盟
        for size in range(1, len(user_ids) + 1):
            for coalition in combinations(user_ids, size):
                coalition_set = set(coalition)

                # 联盟成员的总分摊
                coalition_sharing = sum(sharing[u_id] for u_id in coalition)

                # 联盟单独的成本
                coalition_cost = self.cost_function(coalition_set)

                # 如果分摊超过单独成本，形成阻塞
                if coalition_sharing > coalition_cost + 0.01:
                    blocking_coalitions.append(coalition)

        return len(blocking_coalitions) == 0, blocking_coalitions


def demonstrate_airport_problem():
    """演示经典的机场问题"""
    print("=" * 70)
    print("机场问题 - 成本分摊经典案例")
    print("=" * 70)

    # 3架飞机，需要不同长度的跑道
    # 小飞机1: 1000米, 成本100万
    # 小飞机2: 1500米, 成本130万
    # 大飞机: 2000米, 成本150万

    def airport_cost(user_set):
        """机场成本函数"""
        if not user_set:
            return 0

        # 需要的最大跑道长度
        max_runway = 0
        if 'small1' in user_set:
            max_runway = max(max_runway, 1000)
        if 'small2' in user_set:
            max_runway = max(max_runway, 1500)
        if 'large' in user_set:
            max_runway = max(max_runway, 2000)

        # 成本函数（简化）
        if max_runway <= 1000:
            return 100
        elif max_runway <= 1500:
            return 130
        else:
            return 150

    users = [
        User('small1', usage=1000, value=80),
        User('small2', usage=1500, value=100),
        User('large', usage=2000, value=120)
    ]

    problem = CostSharingProblem(users, airport_cost)

    print("\n场景设置：")
    print("-" * 70)
    print("  小飞机1: 需要1000米跑道")
    print("  小飞机2: 需要1500米跑道")
    print("  大飞机:   需要2000米跑道")
    print("\n  建设成本:")
    print("    1000米跑道: $100万")
    print("    1500米跑道: $130万")
    print("    2000米跑道: $150万")

    # 计算不同分摊方法
    print("\n" + "=" * 70)
    print("不同分摊方法对比")
    print("=" * 70)

    methods = {
        '平均分摊': problem.equal_sharing(),
        '比例分摊': problem.proportional_sharing(),
        '边际成本': problem.marginal_cost_sharing(),
        'Shapley值': problem.shapley_cost_sharing()
    }

    for method_name, sharing in methods.items():
        print(f"\n{method_name}:")
        total = 0
        for user_id in ['small1', 'small2', 'large']:
            cost = sharing.get(user_id, 0)
            print(f"  {user_id:8s}: ${cost:6.2f}万")
            total += cost
        print(f"  总计:     ${total:6.2f}万")

        # 检查性质
        balanced = problem.check_budget_balance(sharing)
        rational = problem.check_individual_rationality(sharing)
        in_core, _ = problem.check_core_membership(sharing)

        print(f"  预算平衡: {balanced}, 个体理性: {rational}, 在核心: {in_core}")

    # 分析
    print("\n" + "=" * 70)
    print("分析")
    print("=" * 70)

    shapley = methods['Shapley值']

    print("\nShapley值的逻辑：")
    print("  - 考虑所有可能的到达顺序")
    print("  - 每个飞机支付其平均边际成本贡献")
    print("\n  示例计算（一个排列）：")
    print("    顺序: small1 → small2 → large")
    print("      small1到达: 成本0→100, 边际$100万")
    print("      small2到达: 成本100→130, 边际$30万")
    print("      large到达: 成本130→150, 边际$20万")
    print("\n  平均所有6种排列后得到Shapley值")


def demonstrate_ride_sharing():
    """演示拼车成本分摊"""
    print("\n" + "=" * 70)
    print("拼车成本分摊")
    print("=" * 70)

    def ride_cost(user_set):
        """拼车成本：固定成本 + 每人可变成本"""
        if not user_set:
            return 0
        return 15 + 3 * len(user_set)  # $15固定 + 每人$3

    users = [
        User('Alice', usage=1, value=25),
        User('Bob', usage=1, value=22),
        User('Carol', usage=1, value=20)
    ]

    problem = CostSharingProblem(users, ride_cost)

    print("\n场景: 3人拼车去机场")
    print(f"  固定成本: $15 (司机费)")
    print(f"  可变成本: $3/人 (燃油)")
    print(f"  总成本: ${ride_cost({'Alice', 'Bob', 'Carol'})}")

    shapley = problem.shapley_cost_sharing()
    print("\nShapley值分摊:")
    for user_id, cost in shapley.items():
        print(f"  {user_id}: ${cost:.2f}")

    print("\n公平性:")
    print(f"  - 每人支付相同（对称性）")
    print(f"  - 固定成本平摊")
    print(f"  - 可变成本各自承担")


if __name__ == '__main__':
    # 演示机场问题
    demonstrate_airport_problem()

    # 演示拼车问题
    demonstrate_ride_sharing()

    # 运行测试
    print("\n" + "=" * 70)
    print("运行单元测试")
    print("=" * 70)

    from app03_cost_sharing import test
    test()
