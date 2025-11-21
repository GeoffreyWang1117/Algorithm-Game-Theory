"""
练习 8: 重复剔除严格劣策略 (Iterated Elimination of Strictly Dominated Strategies)

严格劣策略是指无论对手选择什么策略，都存在另一个策略能够给玩家带来
严格更高效用的策略。理性玩家不会选择严格劣策略。

重复剔除过程 (IESDS):
1. 找出并删除所有严格劣策略
2. 在剩余的博弈中，再次寻找并删除严格劣策略
3. 重复此过程直到无法再删除策略

性质：
- IESDS 的顺序无关性：无论以什么顺序删除，最终结果相同
- 如果 IESDS 后只剩一个策略组合，该组合必定是唯一的纳什均衡
- 所有纳什均衡都能在 IESDS 后存活

任务：实现 IESDS 算法。
"""


def is_strictly_dominated(payoff_matrix, player, strategy, available_strategies):
    """
    判断策略是否被严格劣（在给定可用策略集合中）

    参数:
        payoff_matrix: 支付矩阵
        player: 1 或 2
        strategy: 要检查的策略
        available_strategies: 当前可用的策略 {player: [strategies]}

    返回:
        bool: 是否是严格劣策略
    """
    # TODO: 实现严格劣策略判断
    # 提示：检查是否存在另一个策略，在所有对手策略下都严格更好
    pass


def iterated_elimination(payoff_matrix):
    """
    执行重复剔除严格劣策略

    参数:
        payoff_matrix: 支付矩阵，格式为 {(s1, s2): (u1, u2)}

    返回:
        dict: 剔除后剩余的策略 {player: [strategies]}
    """
    # TODO: 实现 IESDS 算法
    # 1. 初始化所有策略为可用
    # 2. 循环直到无法再删除：
    #    - 对每个玩家，找出严格劣策略
    #    - 删除这些策略
    # 3. 返回剩余策略
    pass


def get_all_strategies(payoff_matrix):
    """
    从支付矩阵中提取所有策略

    参数:
        payoff_matrix: 支付矩阵

    返回:
        dict: {1: [player1_strategies], 2: [player2_strategies]}
    """
    # TODO: 提取所有策略
    pass


# HINT: 策略 s 是严格劣策略，如果存在策略 s'，使得对所有对手策略 t:
#       u(s', t) > u(s, t)
# HINT: IESDS 需要循环执行，每次删除后重新检查


def test():
    """测试函数"""
    from exercise_runner import Color

    print(f"{Color.CYAN}测试 1: 简单的 IESDS{Color.END}")

    # 一个有明确严格劣策略的博弈
    game1 = {
        ('A', 'L'): (3, 1),
        ('A', 'R'): (2, 0),
        ('B', 'L'): (1, 2),
        ('B', 'R'): (0, 1),
        ('C', 'L'): (2, 0),  # C 对玩家1是严格劣策略（被 A 严格占优）
        ('C', 'R'): (1, 2)
    }

    remaining = iterated_elimination(game1)

    # C 应该被删除
    if 'C' not in remaining[1]:
        print(f"  {Color.GREEN}✓{Color.END} 正确删除严格劣策略 C")
        print(f"    剩余策略: P1={remaining[1]}, P2={remaining[2]}")
    else:
        print(f"  {Color.RED}✗{Color.END} C 应该被删除（被 A 严格占优）")
        return False

    print(f"\n{Color.CYAN}测试 2: 多轮 IESDS{Color.END}")

    # 需要多轮才能完全剔除的博弈
    game2 = {
        ('A', 'L'): (4, 3),
        ('A', 'C'): (3, 2),
        ('A', 'R'): (2, 1),
        ('B', 'L'): (3, 1),
        ('B', 'C'): (2, 4),
        ('B', 'R'): (1, 2),
        ('C', 'L'): (2, 0),  # C 是严格劣策略
        ('C', 'C'): (1, 1),
        ('C', 'R'): (0, 0)
    }

    remaining2 = iterated_elimination(game2)

    print(f"    剩余策略: P1={remaining2[1]}, P2={remaining2[2]}")

    # C 应该被删除
    if 'C' not in remaining2[1]:
        print(f"  {Color.GREEN}✓{Color.END} 第一轮正确删除 C")
    else:
        print(f"  {Color.RED}✗{Color.END} C 应该被删除")
        return False

    print(f"\n{Color.CYAN}测试 3: 提取策略{Color.END}")

    strategies = get_all_strategies(game1)

    if set(strategies[1]) == {'A', 'B', 'C'} and set(strategies[2]) == {'L', 'R'}:
        print(f"  {Color.GREEN}✓{Color.END} 正确提取所有策略")
    else:
        print(f"  {Color.RED}✗{Color.END} 策略提取错误")
        print(f"    期望: P1={{A,B,C}}, P2={{L,R}}")
        print(f"    实际: P1={set(strategies[1])}, P2={set(strategies[2])}")
        return False

    print(f"\n{Color.CYAN}测试 4: 囚徒困境（无法剔除）{Color.END}")

    prisoner_dilemma = {
        ('C', 'C'): (-1, -1),
        ('C', 'D'): (-3, 0),
        ('D', 'C'): (0, -3),
        ('D', 'D'): (-2, -2)
    }

    remaining_pd = iterated_elimination(prisoner_dilemma)

    # 在囚徒困境中，C 是严格劣策略（被 D 严格占优）
    if set(remaining_pd[1]) == {'D'} and set(remaining_pd[2]) == {'D'}:
        print(f"  {Color.GREEN}✓{Color.END} IESDS 找到唯一解: (D, D)")
        print(f"  {Color.YELLOW}💡 这也是唯一的纳什均衡！{Color.END}")
    else:
        print(f"  {Color.RED}✗{Color.END} 应该只剩下 D")
        print(f"    实际: P1={remaining_pd[1]}, P2={remaining_pd[2]}")
        return False

    return True


if __name__ == '__main__':
    test()
