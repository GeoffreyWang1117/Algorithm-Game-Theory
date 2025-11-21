"""
练习 10: 混合策略纳什均衡的支撑集 (Support of Mixed Nash Equilibrium)

混合策略纳什均衡的一个关键性质：
在混合策略纳什均衡中，玩家只会在其支撑集（support）中的纯策略之间
进行随机化，而支撑集中的每个策略都必须给玩家带来相同的期望效用。

支撑集：混合策略中概率大于 0 的纯策略集合

无差异原则（Indifference Principle）：
如果玩家在纳什均衡中混合多个策略，那么这些策略必须给玩家带来相同的
期望效用。否则，玩家会只选择效用最高的策略。

任务：实现使用支撑集枚举法求解混合策略纳什均衡。
"""


def is_best_response_mixed(payoff_matrix, player, mixed_strategy, opponent_mixed):
    """
    检查混合策略是否是对手混合策略的最佳响应

    参数:
        payoff_matrix: 支付矩阵
        player: 1 或 2
        mixed_strategy: 该玩家的混合策略 {strategy: probability}
        opponent_mixed: 对手的混合策略 {strategy: probability}

    返回:
        bool: 是否是最佳响应
    """
    # TODO: 实现最佳响应检查
    # 提示：计算支撑集中每个策略的期望效用，应该都相等且是最大的
    pass


def expected_utility_for_pure_strategy(payoff_matrix, player, pure_strategy,
                                       opponent_mixed):
    """
    计算玩家选择某个纯策略对抗对手混合策略时的期望效用

    参数:
        payoff_matrix: 支付矩阵
        player: 1 或 2
        pure_strategy: 玩家的纯策略
        opponent_mixed: 对手的混合策略

    返回:
        float: 期望效用
    """
    # TODO: 实现期望效用计算
    pass


def find_indifferent_probabilities(payoff_matrix, player, support, opponent_strategies):
    """
    使用无差异条件求解使对手无差异的混合策略

    参数:
        payoff_matrix: 支付矩阵
        player: 该玩家
        support: 该玩家在均衡中使用的策略支撑集
        opponent_strategies: 对手需要无差异的策略

    返回:
        dict: 混合策略 {strategy: probability}，如果无解返回 None
    """
    # TODO: 实现无差异概率求解
    # 这是一个线性方程组问题
    # 对于每对对手策略，期望效用应该相等
    pass


def find_mixed_nash_support_enumeration(payoff_matrix):
    """
    使用支撑集枚举法找混合策略纳什均衡

    算法：
    1. 枚举可能的支撑集组合
    2. 对每个支撑集组合：
       - 使用无差异条件求解混合策略
       - 验证是否构成纳什均衡
    3. 返回所有找到的均衡

    参数:
        payoff_matrix: 支付矩阵

    返回:
        list: 所有混合策略纳什均衡
    """
    # TODO: 实现支撑集枚举算法
    # 这是一个进阶练习！可以先尝试实现 2x2 博弈的特殊情况
    pass


# HINT: 无差异原则：如果玩家混合策略 σ 在支撑集 S 上，
#       那么对所有 s, s' ∈ S，EU(s, σ_{-i}) = EU(s', σ_{-i})
# HINT: 对于 2x2 博弈，如果玩家混合两个策略，设概率为 p 和 (1-p)
#       求解使对手无差异的 p 值


def test():
    """测试函数"""
    from exercise_runner import Color
    import math

    print(f"{Color.CYAN}测试 1: 纯策略期望效用{Color.END}")

    game = {
        ('T', 'L'): (3, 1),
        ('T', 'R'): (0, 0),
        ('B', 'L'): (0, 0),
        ('B', 'R'): (1, 3)
    }

    # 玩家2 混合策略：50% L, 50% R
    opponent_mixed = {'L': 0.5, 'R': 0.5}

    eu_T = expected_utility_for_pure_strategy(game, 1, 'T', opponent_mixed)
    eu_B = expected_utility_for_pure_strategy(game, 1, 'B', opponent_mixed)

    expected_eu_T = 0.5 * 3 + 0.5 * 0  # 1.5
    expected_eu_B = 0.5 * 0 + 0.5 * 1  # 0.5

    if abs(eu_T - expected_eu_T) < 0.01 and abs(eu_B - expected_eu_B) < 0.01:
        print(f"  {Color.GREEN}✓{Color.END} 期望效用计算正确")
        print(f"    EU(T) = {eu_T:.2f}, EU(B) = {eu_B:.2f}")
    else:
        print(f"  {Color.RED}✗{Color.END} 期望效用计算错误")
        return False

    print(f"\n{Color.CYAN}测试 2: 匹配硬币的混合纳什均衡{Color.END}")

    matching_pennies = {
        ('H', 'H'): (1, -1),
        ('H', 'T'): (-1, 1),
        ('T', 'H'): (-1, 1),
        ('T', 'T'): (1, -1)
    }

    # 在匹配硬币中，唯一的纳什均衡是双方都 50-50 混合
    p1_mixed = {'H': 0.5, 'T': 0.5}
    p2_mixed = {'H': 0.5, 'T': 0.5}

    # 验证这是最佳响应
    is_br1 = is_best_response_mixed(matching_pennies, 1, p1_mixed, p2_mixed)
    is_br2 = is_best_response_mixed(matching_pennies, 2, p2_mixed, p1_mixed)

    if is_br1 and is_br2:
        print(f"  {Color.GREEN}✓{Color.END} (0.5, 0.5) 是匹配硬币的纳什均衡")
    else:
        print(f"  {Color.RED}✗{Color.END} 最佳响应检查失败")
        return False

    # 验证非均衡策略不是最佳响应
    p1_non_eq = {'H': 0.7, 'T': 0.3}
    is_br_non_eq = is_best_response_mixed(matching_pennies, 2, p2_mixed, p1_non_eq)

    if not is_br_non_eq:
        print(f"  {Color.GREEN}✓{Color.END} 正确识别非均衡策略")
    else:
        print(f"  {Color.RED}✗{Color.END} 应该识别为非均衡")
        return False

    print(f"\n{Color.CYAN}测试 3: 性别战争的混合纳什均衡{Color.END}")

    battle_of_sexes = {
        ('O', 'O'): (2, 1),
        ('O', 'F'): (0, 0),
        ('F', 'O'): (0, 0),
        ('F', 'F'): (1, 2)
    }

    # 性别战争有三个纳什均衡：
    # 1. (O, O) - 纯策略
    # 2. (F, F) - 纯策略
    # 3. 混合策略：P1: (2/3 O, 1/3 F), P2: (1/3 O, 2/3 F)

    # 验证混合策略纳什均衡
    p1_bos = {'O': 2/3, 'F': 1/3}
    p2_bos = {'O': 1/3, 'F': 2/3}

    # 计算 P2 选择 O 和 F 对抗 P1 混合策略的期望效用
    eu_p2_O = expected_utility_for_pure_strategy(battle_of_sexes, 2, 'O', p1_bos)
    eu_p2_F = expected_utility_for_pure_strategy(battle_of_sexes, 2, 'F', p1_bos)

    print(f"    P2 的期望效用: EU(O) = {eu_p2_O:.3f}, EU(F) = {eu_p2_F:.3f}")

    # 在均衡中，P2 应该对 O 和 F 无差异
    if abs(eu_p2_O - eu_p2_F) < 0.01:
        print(f"  {Color.GREEN}✓{Color.END} P2 对两个策略无差异（无差异原则）")
    else:
        print(f"  {Color.RED}✗{Color.END} P2 应该对两个策略无差异")
        return False

    print(f"\n{Color.YELLOW}💡 关键洞察：{Color.END}")
    print(f"{Color.YELLOW}   在混合纳什均衡中，每个玩家的混合是为了让对手无差异！{Color.END}")
    print(f"{Color.YELLOW}   而不是为了自己无差异（虽然自己也确实无差异）{Color.END}")

    return True


if __name__ == '__main__':
    test()
