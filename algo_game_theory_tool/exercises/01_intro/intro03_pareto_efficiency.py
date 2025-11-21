"""
练习 7: 帕累托效率 (Pareto Efficiency)

帕累托效率是经济学和博弈论中的重要概念。一个结果是帕累托有效的，
如果不存在其他结果能够在不让任何人变差的情况下让至少一个人变好。

定义：策略组合 s 是帕累托有效的，如果不存在另一个策略组合 s'，使得：
- 对所有玩家 i: u_i(s') >= u_i(s)
- 至少存在一个玩家 j: u_j(s') > u_j(s)

如果存在这样的 s'，我们说 s' 帕累托占优 (Pareto dominates) s。

任务：实现判断帕累托效率的函数。
"""


def is_pareto_efficient(payoff_matrix, strategy_profile):
    """
    判断给定策略组合是否帕累托有效

    参数:
        payoff_matrix: 支付矩阵，格式为 {(s1, s2): (u1, u2)}
        strategy_profile: 策略组合，格式为 (s1, s2)

    返回:
        bool: 是否帕累托有效
    """
    # TODO: 实现帕累托效率判断
    # 检查是否存在其他策略组合帕累托占优当前策略
    pass


def find_pareto_efficient_outcomes(payoff_matrix):
    """
    找出所有帕累托有效的结果

    参数:
        payoff_matrix: 支付矩阵

    返回:
        list: 所有帕累托有效的策略组合列表
    """
    # TODO: 实现找出所有帕累托有效结果
    pass


def pareto_dominates(payoff_matrix, strategy1, strategy2):
    """
    判断 strategy1 是否帕累托占优 strategy2

    参数:
        payoff_matrix: 支付矩阵
        strategy1: 策略组合1
        strategy2: 策略组合2

    返回:
        bool: strategy1 是否帕累托占优 strategy2
    """
    # TODO: 实现帕累托占优判断
    # strategy1 帕累托占优 strategy2 当且仅当：
    # 1. 每个玩家在 strategy1 下的效用 >= strategy2
    # 2. 至少有一个玩家在 strategy1 下严格更好
    pass


# HINT: 一个结果是帕累托有效的，如果没有其他结果帕累托占优它
# HINT: 检查所有其他策略组合，看是否有帕累托占优关系


def test():
    """测试函数"""
    from exercise_runner import Color

    print(f"{Color.CYAN}测试 1: 囚徒困境的帕累托效率{Color.END}")

    prisoner_dilemma = {
        ('C', 'C'): (-1, -1),  # 帕累托有效
        ('C', 'D'): (-3, 0),
        ('D', 'C'): (0, -3),
        ('D', 'D'): (-2, -2)   # 纳什均衡但不帕累托有效
    }

    # (C, C) 是帕累托有效的
    is_cc_efficient = is_pareto_efficient(prisoner_dilemma, ('C', 'C'))
    # (D, D) 不是帕累托有效的（被 (C, C) 帕累托占优）
    is_dd_efficient = is_pareto_efficient(prisoner_dilemma, ('D', 'D'))

    if is_cc_efficient and not is_dd_efficient:
        print(f"  {Color.GREEN}✓{Color.END} 正确判断帕累托效率")
        print(f"    (C, C) 是帕累托有效的")
        print(f"    (D, D) 不是帕累托有效的")
    else:
        print(f"  {Color.RED}✗{Color.END} 帕累托效率判断错误")
        print(f"    (C, C): {is_cc_efficient}，应该是 True")
        print(f"    (D, D): {is_dd_efficient}，应该是 False")
        return False

    print(f"\n{Color.CYAN}测试 2: 帕累托占优关系{Color.END}")

    # (C, C) 帕累托占优 (D, D)
    cc_dominates_dd = pareto_dominates(prisoner_dilemma, ('C', 'C'), ('D', 'D'))

    if cc_dominates_dd:
        print(f"  {Color.GREEN}✓{Color.END} (C, C) 帕累托占优 (D, D)")
    else:
        print(f"  {Color.RED}✗{Color.END} (C, C) 应该帕累托占优 (D, D)")
        return False

    # (C, D) 不帕累托占优 (D, D)
    cd_dominates_dd = pareto_dominates(prisoner_dilemma, ('C', 'D'), ('D', 'D'))

    if not cd_dominates_dd:
        print(f"  {Color.GREEN}✓{Color.END} (C, D) 不帕累托占优 (D, D)")
    else:
        print(f"  {Color.RED}✗{Color.END} (C, D) 不应该帕累托占优 (D, D)")
        return False

    print(f"\n{Color.CYAN}测试 3: 找出所有帕累托有效结果{Color.END}")

    pareto_efficient = find_pareto_efficient_outcomes(prisoner_dilemma)
    pareto_efficient_set = set(pareto_efficient)

    # 囚徒困境中，只有 (C, C), (C, D), (D, C) 是帕累托有效的
    expected = {('C', 'C'), ('C', 'D'), ('D', 'C')}

    if pareto_efficient_set == expected:
        print(f"  {Color.GREEN}✓{Color.END} 找到所有帕累托有效结果:")
        for outcome in sorted(pareto_efficient):
            payoff = prisoner_dilemma[outcome]
            print(f"    {outcome}: {payoff}")
    else:
        print(f"  {Color.RED}✗{Color.END} 帕累托有效结果不正确")
        print(f"    期望: {expected}")
        print(f"    实际: {pareto_efficient_set}")
        return False

    print(f"\n{Color.YELLOW}💡 观察：纳什均衡 (D, D) 不是帕累托有效的！{Color.END}")
    print(f"{Color.YELLOW}   这展示了个体理性和集体理性的冲突。{Color.END}")

    return True


if __name__ == '__main__':
    test()
