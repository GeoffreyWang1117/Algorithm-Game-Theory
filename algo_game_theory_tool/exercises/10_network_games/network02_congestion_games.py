"""
练习 16: 拥塞博弈 (Congestion Games)

拥塞博弈由 Rosenthal (1973) 提出，是势博弈的重要子类。

定义：n 个玩家，每个玩家从策略集中选择一个子集。
每个资源 e 有成本函数 c_e(k)，k 是使用该资源的玩家数量。
玩家 i 选择策略 S_i 的成本 = Σ_{e ∈ S_i} c_e(k_e)

关键性质：
1. 所有拥塞博弈都是势博弈
2. 势函数：Φ(s) = Σ_e Σ_{j=1}^{k_e} c_e(j)
3. 纯策略纳什均衡总是存在
4. 最佳响应动态保证收敛

经典例子：
- 路由选择：玩家选择路径，边有拥塞成本
- 资源分配：玩家选择服务器，服务器有负载成本

任务：实现拥塞博弈并验证其是势博弈。
"""


class CongestionGame:
    """拥塞博弈"""

    def __init__(self, n_players, resources, strategies, cost_functions):
        """
        初始化拥塞博弈

        参数:
            n_players: 玩家数量
            resources: 资源列表
            strategies: 每个玩家的策略集 {player: [strategies]}
                       每个策略是资源的子集
            cost_functions: 成本函数 {resource: function(k)}
                           k 是使用该资源的玩家数
        """
        # TODO: 初始化拥塞博弈
        pass

    def compute_cost(self, player, strategy_profile):
        """
        计算玩家在给定策略组合下的成本

        参数:
            player: 玩家 ID
            strategy_profile: 策略组合 {player: strategy}

        返回:
            float: 玩家成本
        """
        # TODO: 计算玩家成本
        # 成本 = Σ_{e ∈ S_i} c_e(k_e)
        # 其中 k_e 是使用资源 e 的玩家数
        pass


def compute_resource_usage(strategy_profile, strategies):
    """
    计算每个资源被多少玩家使用

    参数:
        strategy_profile: 策略组合 {player: strategy_index}
        strategies: 策略定义 {player: [strategies]}

    返回:
        dict: {resource: count}
    """
    # TODO: 计算资源使用情况
    pass


def compute_potential_function_congestion(strategy_profile, resources,
                                         strategies, cost_functions):
    """
    计算拥塞博弈的势函数

    势函数：Φ(s) = Σ_e Σ_{j=1}^{k_e} c_e(j)
    其中 k_e 是在策略组合 s 下使用资源 e 的玩家数

    直觉：势函数是"累积成本"，考虑了每个玩家依次加入时的成本

    参数:
        strategy_profile: 策略组合
        resources: 资源列表
        strategies: 策略定义
        cost_functions: 成本函数

    返回:
        float: 势函数值
    """
    # TODO: 计算势函数
    # Φ = Σ_e [c_e(1) + c_e(2) + ... + c_e(k_e)]
    pass


def verify_potential_game_property(game, strategy_profile, player,
                                   new_strategy):
    """
    验证势博弈性质：
    Φ(s'_i, s_{-i}) - Φ(s_i, s_{-i}) = u_i(s'_i, s_{-i}) - u_i(s_i, s_{-i})

    参数:
        game: 拥塞博弈对象
        strategy_profile: 当前策略组合
        player: 改变策略的玩家
        new_strategy: 新策略

    返回:
        bool: 是否满足势博弈性质
    """
    # TODO: 验证势博弈性质
    pass


def find_nash_equilibrium_congestion(game):
    """
    在拥塞博弈中找纳什均衡

    方法：找势函数的最小值点（对于成本最小化）

    参数:
        game: 拥塞博弈

    返回:
        dict: 纳什均衡策略组合
    """
    # TODO: 找纳什均衡
    # 枚举所有策略组合，找势函数最小的
    pass


# HINT: 拥塞博弈的势函数不是社会成本！
# HINT: 社会成本 = Σ_e k_e * c_e(k_e)
# HINT: 势函数 = Σ_e Σ_{j=1}^{k_e} c_e(j)
# HINT: 两者不同！但势函数的最小值点是纳什均衡


def test():
    """测试函数"""
    from exercise_runner import Color

    print(f"{Color.CYAN}测试 1: 简单的两玩家拥塞博弈{Color.END}")

    # 两个玩家，两个资源（路径）
    # 玩家1和2都要从 s 到 t
    # 路径1：资源 {A}，成本 c_A(k) = k
    # 路径2：资源 {B}，成本 c_B(k) = 3（常数）

    resources = ['A', 'B']
    strategies = {
        1: [['A'], ['B']],  # 玩家1可选路径A或B
        2: [['A'], ['B']]   # 玩家2可选路径A或B
    }
    cost_functions = {
        'A': lambda k: k,   # 线性拥塞
        'B': lambda k: 3    # 常数成本
    }

    game = CongestionGame(2, resources, strategies, cost_functions)

    print(f"  {Color.GREEN}✓{Color.END} 拥塞博弈构建成功")

    print(f"\n{Color.CYAN}测试 2: 计算玩家成本{Color.END}")

    # 策略组合：玩家1选A（策略0），玩家2选A（策略0）
    profile1 = {1: 0, 2: 0}  # 都选 A

    # 玩家1的成本：c_A(2) = 2（因为两人都在A上）
    # 玩家2的成本：c_A(2) = 2

    try:
        cost1 = game.compute_cost(1, profile1)
        cost2 = game.compute_cost(2, profile1)

        if abs(cost1 - 2) < 0.001 and abs(cost2 - 2) < 0.001:
            print(f"  {Color.GREEN}✓{Color.END} 成本计算正确")
            print(f"    玩家1成本: {cost1}")
            print(f"    玩家2成本: {cost2}")
        else:
            print(f"  {Color.RED}✗{Color.END} 成本计算错误")
            return False
    except:
        print(f"  {Color.YELLOW}提示：完成 compute_cost 实现{Color.END}")

    print(f"\n{Color.CYAN}测试 3: 势函数计算{Color.END}")

    # 策略组合：(A, A)
    # 势函数：Φ = c_A(1) + c_A(2) = 1 + 2 = 3

    try:
        potential = compute_potential_function_congestion(
            profile1, resources, strategies, cost_functions
        )

        if abs(potential - 3) < 0.001:
            print(f"  {Color.GREEN}✓{Color.END} 势函数: Φ(A,A) = {potential}")
        else:
            print(f"  {Color.RED}✗{Color.END} 势函数错误，期望3")
            return False
    except:
        print(f"  {Color.YELLOW}提示：完成势函数实现{Color.END}")

    print(f"\n{Color.CYAN}测试 4: 验证势博弈性质{Color.END}")

    # 玩家1从A改到B
    # ΔΦ 应该等于 Δu_1

    print(f"  {Color.YELLOW}理论验证：{Color.END}")
    print(f"    状态 (A, A):")
    print(f"      Φ = c_A(1) + c_A(2) = 1 + 2 = 3")
    print(f"      u_1 = c_A(2) = 2")
    print(f"    ")
    print(f"    玩家1改为B -> (B, A):")
    print(f"      Φ = c_A(1) + c_B(1) = 1 + 3 = 4")
    print(f"      u_1 = c_B(1) = 3")
    print(f"    ")
    print(f"    ΔΦ = 4 - 3 = 1")
    print(f"    Δu_1 = 3 - 2 = 1")
    print(f"    {Color.GREEN}✓ ΔΦ = Δu_1（势博弈性质）{Color.END}")

    print(f"\n{Color.CYAN}测试 5: 找纳什均衡{Color.END}")

    # 分析所有策略组合：
    print(f"  {Color.YELLOW}策略组合分析：{Color.END}")
    print(f"    (A, A): 成本 (2, 2), Φ = 3")
    print(f"    (A, B): 成本 (1, 3), Φ = 4")
    print(f"    (B, A): 成本 (3, 1), Φ = 4")
    print(f"    (B, B): 成本 (3, 3), Φ = 6")
    print(f"    ")
    print(f"    势函数最小值：(A, A)，Φ = 3")
    print(f"    ")
    print(f"    验证 (A, A) 是纳什均衡：")
    print(f"      玩家1偏离到B：成本 2 -> 3（变差）")
    print(f"      玩家2偏离到B：成本 2 -> 3（变差）")
    print(f"    {Color.GREEN}✓ (A, A) 是纳什均衡{Color.END}")

    print(f"\n{Color.CYAN}测试 6: 社会成本 vs 势函数{Color.END}")

    print(f"  {Color.YELLOW}重要区别：{Color.END}")
    print(f"    社会成本 = Σ k_e * c_e(k_e)")
    print(f"    势函数   = Σ Σ_{j=1}^{{k_e}} c_e(j)")
    print(f"    ")
    print(f"    对于 (A, A):")
    print(f"      社会成本 = 2 * c_A(2) = 2 * 2 = 4")
    print(f"      势函数   = c_A(1) + c_A(2) = 1 + 2 = 3")
    print(f"    ")
    print(f"    {Color.RED}两者不同！{Color.END}")
    print(f"    势函数的最小值点是纳什均衡")
    print(f"    但不一定是社会最优")

    print(f"\n{Color.CYAN}测试 7: Rosenthal 定理{Color.END}")

    print(f"  {Color.YELLOW}Rosenthal (1973) 定理：{Color.END}")
    print(f"    所有拥塞博弈都是精确势博弈")
    print(f"    ")
    print(f"    推论：")
    print(f"    1. 纯策略纳什均衡总是存在")
    print(f"    2. 最佳响应动态有限步收敛")
    print(f"    3. 可以通过最小化势函数找均衡")

    print(f"\n{Color.YELLOW}💡 拥塞博弈的重要性：{Color.END}")
    print(f"{Color.YELLOW}   - 建模网络拥塞、资源竞争{Color.END}")
    print(f"{Color.YELLOW}   - 保证纳什均衡存在（势博弈性质）{Color.END}")
    print(f"{Color.YELLOW}   - 最佳响应动态收敛（实际可达到均衡）{Color.END}")
    print(f"{Color.YELLOW}   - 应用：交通路由、负载均衡、频谱分配{Color.END}")

    return True


if __name__ == '__main__':
    test()
