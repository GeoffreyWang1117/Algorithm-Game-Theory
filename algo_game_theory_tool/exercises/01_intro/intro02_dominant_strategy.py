"""
练习 2: 占优策略 (Dominant Strategy)

占优策略是博弈论中的核心概念。如果一个策略无论对手选择什么策略，
都能给玩家带来更高的效用，那么这个策略就是占优策略。

严格占优策略 (Strictly Dominant): s 严格优于所有其他策略
弱占优策略 (Weakly Dominant): s 不严格劣于任何策略，且至少对某个对手策略严格优

任务：实现函数来判断一个策略是否是占优策略。
"""


def has_dominant_strategy(payoff_matrix, player):
    """
    判断指定玩家是否有占优策略（严格占优）

    参数:
        payoff_matrix: 支付矩阵，格式为 {(s1, s2): (u1, u2)}
        player: 1 或 2，表示玩家1或玩家2

    返回:
        dominant_strategy: 占优策略，如果不存在则返回 None
    """
    # TODO: 实现判断占优策略的逻辑
    # 提示：需要比较玩家的每个策略在所有对手策略下的效用
    pass


def is_strictly_dominated(payoff_matrix, player, strategy):
    """
    判断指定策略是否被严格占优（即是否是严格劣策略）

    参数:
        payoff_matrix: 支付矩阵，格式为 {(s1, s2): (u1, u2)}
        player: 1 或 2，表示玩家1或玩家2
        strategy: 要检查的策略

    返回:
        bool: 如果该策略被严格占优则返回 True
    """
    # TODO: 实现判断严格劣策略的逻辑
    pass


# HINT: 对于玩家1，占优策略 s 意味着对于所有的 s' != s 和所有的 t，
#       都有 u1(s, t) > u1(s', t)
# HINT: 可以先提取出该玩家的所有策略，然后逐一比较


def test():
    """测试函数"""
    from exercise_runner import Color

    print(f"{Color.CYAN}测试 1: 囚徒困境 - 玩家1的占优策略{Color.END}")

    # 囚徒困境中，背叛(D)是占优策略
    prisoner_dilemma = {
        ('C', 'C'): (-1, -1),
        ('C', 'D'): (-3, 0),
        ('D', 'C'): (0, -3),
        ('D', 'D'): (-2, -2)
    }

    dominant1 = has_dominant_strategy(prisoner_dilemma, 1)
    dominant2 = has_dominant_strategy(prisoner_dilemma, 2)

    if dominant1 == 'D':
        print(f"  {Color.GREEN}✓{Color.END} 玩家1的占优策略: D")
    else:
        print(f"  {Color.RED}✗{Color.END} 错误: 玩家1的占优策略应该是 D，得到 {dominant1}")
        return False

    if dominant2 == 'D':
        print(f"  {Color.GREEN}✓{Color.END} 玩家2的占优策略: D")
    else:
        print(f"  {Color.RED}✗{Color.END} 错误: 玩家2的占优策略应该是 D，得到 {dominant2}")
        return False

    print(f"\n{Color.CYAN}测试 2: 检查严格劣策略{Color.END}")

    # 在囚徒困境中，合作(C)是严格劣策略
    is_dominated_c1 = is_strictly_dominated(prisoner_dilemma, 1, 'C')
    is_dominated_d1 = is_strictly_dominated(prisoner_dilemma, 1, 'D')

    if is_dominated_c1 and not is_dominated_d1:
        print(f"  {Color.GREEN}✓{Color.END} 正确识别了严格劣策略")
    else:
        print(f"  {Color.RED}✗{Color.END} 严格劣策略判断错误")
        return False

    print(f"\n{Color.CYAN}测试 3: 无占优策略的博弈{Color.END}")

    # 石头剪刀布 - 没有占优策略
    rock_paper_scissors = {
        ('R', 'R'): (0, 0),
        ('R', 'P'): (-1, 1),
        ('R', 'S'): (1, -1),
        ('P', 'R'): (1, -1),
        ('P', 'P'): (0, 0),
        ('P', 'S'): (-1, 1),
        ('S', 'R'): (-1, 1),
        ('S', 'P'): (1, -1),
        ('S', 'S'): (0, 0)
    }

    dominant_rps = has_dominant_strategy(rock_paper_scissors, 1)

    if dominant_rps is None:
        print(f"  {Color.GREEN}✓{Color.END} 正确判断：石头剪刀布没有占优策略")
    else:
        print(f"  {Color.RED}✗{Color.END} 错误: 石头剪刀布不应该有占优策略")
        return False

    return True


if __name__ == '__main__':
    test()
