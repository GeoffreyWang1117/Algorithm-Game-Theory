"""
练习 11: 无政府代价 (Price of Anarchy)

无政府代价 (PoA) 是衡量自私行为导致的效率损失的核心概念，
由 Koutsoupias 和 Papadimitriou (1999) 提出。

定义：PoA 是最优社会福利与最坏纳什均衡社会福利的比值。

$$\\text{PoA} = \\frac{\\max_{s} SW(s)}{\\min_{s \\in NE} SW(s)}$$

其中：
- SW(s) 是策略组合 s 的社会福利（所有玩家效用之和）
- NE 是所有纳什均衡的集合

PoA >= 1，越接近1表示效率损失越小。

任务：实现计算社会福利和无政府代价的函数。
"""


def calculate_social_welfare(payoff_matrix, strategy_profile):
    """
    计算给定策略组合的社会福利（所有玩家效用之和）

    参数:
        payoff_matrix: 支付矩阵 {(s1, s2): (u1, u2)}
        strategy_profile: 策略组合 (s1, s2)

    返回:
        float: 社会福利
    """
    # TODO: 实现社会福利计算
    # 提示：社会福利 = Σ u_i(s)
    pass


def find_optimal_welfare(payoff_matrix):
    """
    找出最优社会福利（所有策略组合中的最大值）

    参数:
        payoff_matrix: 支付矩阵

    返回:
        tuple: (optimal_welfare, optimal_strategy)
    """
    # TODO: 实现寻找最优社会福利
    pass


def calculate_price_of_anarchy(payoff_matrix, nash_equilibria):
    """
    计算无政府代价

    参数:
        payoff_matrix: 支付矩阵
        nash_equilibria: 纳什均衡列表 [strategy_profile, ...]

    返回:
        float: 无政府代价（PoA）
    """
    # TODO: 实现 PoA 计算
    # PoA = 最优社会福利 / 最坏纳什均衡的社会福利
    pass


def calculate_price_of_stability(payoff_matrix, nash_equilibria):
    """
    计算稳定代价 (Price of Stability)

    PoS 是最优社会福利与最好纳什均衡社会福利的比值：
    $$\\text{PoS} = \\frac{\\max_{s} SW(s)}{\\max_{s \\in NE} SW(s)}$$

    PoS <= PoA，衡量通过协调选择最好的均衡能达到的效率

    参数:
        payoff_matrix: 支付矩阵
        nash_equilibria: 纳什均衡列表

    返回:
        float: 稳定代价（PoS）
    """
    # TODO: 实现 PoS 计算
    pass


# HINT: 社会福利 = u1 + u2 + ... + un
# HINT: PoA = OPT / worst_NE，其中 OPT 是社会最优
# HINT: 囚徒困境的 PoA > 1（纳什均衡不是社会最优）


def test():
    """测试函数"""
    from exercise_runner import Color

    print(f"{Color.CYAN}测试 1: 囚徒困境的社会福利{Color.END}")

    prisoner_dilemma = {
        ('C', 'C'): (-1, -1),
        ('C', 'D'): (-3, 0),
        ('D', 'C'): (0, -3),
        ('D', 'D'): (-2, -2)
    }

    sw_cc = calculate_social_welfare(prisoner_dilemma, ('C', 'C'))
    sw_dd = calculate_social_welfare(prisoner_dilemma, ('D', 'D'))

    if abs(sw_cc - (-2)) < 0.001 and abs(sw_dd - (-4)) < 0.001:
        print(f"  {Color.GREEN}✓{Color.END} 社会福利计算正确")
        print(f"    SW(C,C) = {sw_cc}")
        print(f"    SW(D,D) = {sw_dd}")
    else:
        print(f"  {Color.RED}✗{Color.END} 社会福利计算错误")
        print(f"    期望: SW(C,C)=-2, SW(D,D)=-4")
        print(f"    实际: SW(C,C)={sw_cc}, SW(D,D)={sw_dd}")
        return False

    print(f"\n{Color.CYAN}测试 2: 找出最优社会福利{Color.END}")

    opt_welfare, opt_strategy = find_optimal_welfare(prisoner_dilemma)

    if opt_strategy == ('C', 'C') and abs(opt_welfare - (-2)) < 0.001:
        print(f"  {Color.GREEN}✓{Color.END} 最优策略: {opt_strategy}, 福利: {opt_welfare}")
    else:
        print(f"  {Color.RED}✗{Color.END} 最优策略错误")
        print(f"    期望: (C,C), 福利=-2")
        print(f"    实际: {opt_strategy}, 福利={opt_welfare}")
        return False

    print(f"\n{Color.CYAN}测试 3: 计算无政府代价{Color.END}")

    # 囚徒困境的唯一纳什均衡是 (D, D)
    nash_eq = [('D', 'D')]
    poa = calculate_price_of_anarchy(prisoner_dilemma, nash_eq)

    # PoA = SW(C,C) / SW(D,D) = -2 / -4 = 0.5
    # 但在成本最小化中，通常定义为 worst_cost / opt_cost = 4/2 = 2
    # 在效用最大化中，PoA = OPT / worst_NE
    # 这里 OPT = -2, worst_NE = -4
    # PoA = |-2| / |-4| = 2（取绝对值后的比率）
    expected_poa = 2.0

    if abs(poa - expected_poa) < 0.001:
        print(f"  {Color.GREEN}✓{Color.END} 无政府代价: {poa}")
        print(f"  {Color.YELLOW}💡 囚徒困境的 PoA = 2{Color.END}")
        print(f"  {Color.YELLOW}   纳什均衡的效率只有最优的50%{Color.END}")
    else:
        print(f"  {Color.RED}✗{Color.END} PoA 计算错误")
        print(f"    期望: {expected_poa}")
        print(f"    实际: {poa}")
        return False

    print(f"\n{Color.CYAN}测试 4: 协调博弈的 PoA 和 PoS{Color.END}")

    coordination_game = {
        ('A', 'A'): (10, 10),
        ('A', 'B'): (0, 0),
        ('B', 'A'): (0, 0),
        ('B', 'B'): (5, 5)
    }

    # 纳什均衡：(A, A) 和 (B, B)
    nash_eq_coord = [('A', 'A'), ('B', 'B')]

    poa_coord = calculate_price_of_anarchy(coordination_game, nash_eq_coord)
    pos_coord = calculate_price_of_stability(coordination_game, nash_eq_coord)

    # OPT = SW(A,A) = 20
    # worst_NE = SW(B,B) = 10
    # best_NE = SW(A,A) = 20
    # PoA = 20/10 = 2, PoS = 20/20 = 1

    if abs(poa_coord - 2.0) < 0.001 and abs(pos_coord - 1.0) < 0.001:
        print(f"  {Color.GREEN}✓{Color.END} PoA = {poa_coord}, PoS = {pos_coord}")
        print(f"  {Color.YELLOW}💡 PoS = 1 说明存在效率最优的均衡{Color.END}")
        print(f"  {Color.YELLOW}   但玩家可能协调失败选择差的均衡{Color.END}")
    else:
        print(f"  {Color.RED}✗{Color.END} PoA/PoS 计算错误")
        return False

    print(f"\n{Color.CYAN}测试 5: 完美协调博弈{Color.END}")

    # 所有纳什均衡都是社会最优
    perfect_game = {
        ('X', 'X'): (5, 5),
        ('X', 'Y'): (0, 0),
        ('Y', 'X'): (0, 0),
        ('Y', 'Y'): (5, 5)
    }

    nash_eq_perfect = [('X', 'X'), ('Y', 'Y')]
    poa_perfect = calculate_price_of_anarchy(perfect_game, nash_eq_perfect)

    if abs(poa_perfect - 1.0) < 0.001:
        print(f"  {Color.GREEN}✓{Color.END} 完美博弈的 PoA = 1（无效率损失）")
    else:
        print(f"  {Color.RED}✗{Color.END} PoA 应该为 1")
        return False

    return True


if __name__ == '__main__':
    test()
