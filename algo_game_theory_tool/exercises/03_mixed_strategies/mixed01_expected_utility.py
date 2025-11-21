"""
练习 4: 混合策略与期望效用 (Mixed Strategies and Expected Utility)

当博弈没有纯策略纳什均衡时，我们需要考虑混合策略。混合策略是对纯策略
的概率分布。

混合策略纳什均衡：每个玩家随机选择策略，使得：
1. 每个玩家对对手的混合策略都在最佳响应
2. 期望效用不能通过改变策略而提高

期望效用计算：
EU_i(σ_i, σ_{-i}) = Σ_{s∈S} σ_i(s_i) * σ_{-i}(s_{-i}) * u_i(s_i, s_{-i})

任务：实现混合策略的期望效用计算。
"""


def calculate_expected_utility(payoff_matrix, player, prob_dist_p1, prob_dist_p2):
    """
    计算混合策略下的期望效用

    参数:
        payoff_matrix: 支付矩阵，格式为 {(s1, s2): (u1, u2)}
        player: 1 或 2
        prob_dist_p1: 玩家1的混合策略，格式为 {strategy: probability}
        prob_dist_p2: 玩家2的混合策略，格式为 {strategy: probability}

    返回:
        float: 期望效用
    """
    # TODO: 实现期望效用计算
    # 提示：遍历所有策略组合，将概率乘以对应效用
    pass


def find_mixed_nash_2x2(payoff_matrix):
    """
    找出 2x2 博弈的混合策略纳什均衡

    对于 2x2 博弈，如果没有纯策略纳什均衡，一定存在混合策略纳什均衡。
    可以通过让对手对自己的两个纯策略无差异来求解。

    参数:
        payoff_matrix: 支付矩阵，必须是 2x2 博弈

    返回:
        tuple: (prob_dist_p1, prob_dist_p2) 两个玩家的混合策略
    """
    # TODO: 实现 2x2 混合策略纳什均衡求解
    # 提示：设玩家1以概率p选择第一个策略，以(1-p)选择第二个策略
    #       找到使玩家2对两个策略无差异的p值
    pass


# HINT: 期望效用 = Σ P(s1) * P(s2) * u(s1, s2)
# HINT: 对于 2x2 博弈的混合纳什均衡：
#       玩家1的混合策略应该让玩家2对其两个纯策略无差异
#       即：EU_2(p1, s2_1) = EU_2(p1, s2_2)


def test():
    """测试函数"""
    from exercise_runner import Color

    print(f"{Color.CYAN}测试 1: 期望效用计算{Color.END}")

    # 简单的 2x2 博弈
    game = {
        ('A', 'L'): (3, 1),
        ('A', 'R'): (0, 0),
        ('B', 'L'): (1, 0),
        ('B', 'R'): (2, 2)
    }

    # 玩家1: 50% A, 50% B
    # 玩家2: 50% L, 50% R
    prob1 = {'A': 0.5, 'B': 0.5}
    prob2 = {'L': 0.5, 'R': 0.5}

    eu1 = calculate_expected_utility(game, 1, prob1, prob2)
    eu2 = calculate_expected_utility(game, 2, prob1, prob2)

    expected_eu1 = 0.5 * 0.5 * 3 + 0.5 * 0.5 * 0 + 0.5 * 0.5 * 1 + 0.5 * 0.5 * 2
    expected_eu2 = 0.5 * 0.5 * 1 + 0.5 * 0.5 * 0 + 0.5 * 0.5 * 0 + 0.5 * 0.5 * 2

    if abs(eu1 - expected_eu1) < 0.001 and abs(eu2 - expected_eu2) < 0.001:
        print(f"  {Color.GREEN}✓{Color.END} 期望效用计算正确")
        print(f"    玩家1期望效用: {eu1:.2f}")
        print(f"    玩家2期望效用: {eu2:.2f}")
    else:
        print(f"  {Color.RED}✗{Color.END} 期望效用计算错误")
        print(f"    期望: P1={expected_eu1:.2f}, P2={expected_eu2:.2f}")
        print(f"    实际: P1={eu1:.2f}, P2={eu2:.2f}")
        return False

    print(f"\n{Color.CYAN}测试 2: 匹配硬币 (Matching Pennies) 的混合纳什均衡{Color.END}")

    # 匹配硬币：没有纯策略纳什均衡
    matching_pennies = {
        ('H', 'H'): (1, -1),
        ('H', 'T'): (-1, 1),
        ('T', 'H'): (-1, 1),
        ('T', 'T'): (1, -1)
    }

    try:
        mixed_ne = find_mixed_nash_2x2(matching_pennies)
        prob1_ne, prob2_ne = mixed_ne

        # 匹配硬币的混合纳什均衡是 (0.5, 0.5) for both players
        p1_h = prob1_ne.get('H', 0)
        p2_h = prob2_ne.get('H', 0)

        if abs(p1_h - 0.5) < 0.01 and abs(p2_h - 0.5) < 0.01:
            print(f"  {Color.GREEN}✓{Color.END} 找到混合纳什均衡")
            print(f"    玩家1: H={p1_h:.2f}, T={1-p1_h:.2f}")
            print(f"    玩家2: H={p2_h:.2f}, T={1-p2_h:.2f}")
        else:
            print(f"  {Color.RED}✗{Color.END} 混合纳什均衡不正确")
            print(f"    期望: 各 50% 的概率")
            print(f"    实际: P1_H={p1_h:.2f}, P2_H={p2_h:.2f}")
            return False
    except Exception as e:
        print(f"  {Color.RED}✗{Color.END} 错误: {str(e)}")
        return False

    return True


if __name__ == '__main__':
    test()
