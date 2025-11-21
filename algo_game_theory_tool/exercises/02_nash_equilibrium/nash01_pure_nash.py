"""
练习 3: 纯策略纳什均衡 (Pure Strategy Nash Equilibrium)

纳什均衡是博弈论中最重要的解概念。一个策略组合是纳什均衡，当且仅当
没有任何玩家能够通过单方面改变策略来提高自己的效用。

在纯策略纳什均衡中，每个玩家选择一个确定的策略。

数学定义：策略组合 (s1*, s2*) 是纳什均衡，如果：
- u1(s1*, s2*) >= u1(s1, s2*) 对所有 s1
- u2(s1*, s2*) >= u2(s1*, s2) 对所有 s2

任务：实现函数来找出所有纯策略纳什均衡。
"""


def find_pure_nash_equilibria(payoff_matrix):
    """
    找出所有纯策略纳什均衡

    参数:
        payoff_matrix: 支付矩阵，格式为 {(s1, s2): (u1, u2)}

    返回:
        list: 所有纳什均衡的列表，每个元素是策略对 (s1, s2)
    """
    # TODO: 实现寻找纯策略纳什均衡的算法
    # 提示：对于每个策略组合，检查是否每个玩家都在最佳响应
    pass


def is_best_response(payoff_matrix, player, strategy, opponent_strategy):
    """
    判断某个策略是否是对手策略的最佳响应

    参数:
        payoff_matrix: 支付矩阵
        player: 1 或 2
        strategy: 该玩家的策略
        opponent_strategy: 对手的策略

    返回:
        bool: 是否是最佳响应
    """
    # TODO: 实现最佳响应判断
    pass


def get_best_responses(payoff_matrix, player, opponent_strategy):
    """
    获取对手某个策略的所有最佳响应

    参数:
        payoff_matrix: 支付矩阵
        player: 1 或 2
        opponent_strategy: 对手的策略

    返回:
        list: 所有最佳响应策略的列表
    """
    # TODO: 实现获取所有最佳响应
    pass


# HINT: 纳什均衡 = 双方都在最佳响应
# HINT: 可以用下划线法 (underline method)：
#       1. 对玩家1的每个策略，在每列中找到最大效用并标记
#       2. 对玩家2的每个策略，在每行中找到最大效用并标记
#       3. 两个标记都有的格子就是纳什均衡


def test():
    """测试函数"""
    from exercise_runner import Color

    print(f"{Color.CYAN}测试 1: 囚徒困境{Color.END}")

    prisoner_dilemma = {
        ('C', 'C'): (-1, -1),
        ('C', 'D'): (-3, 0),
        ('D', 'C'): (0, -3),
        ('D', 'D'): (-2, -2)
    }

    ne = find_pure_nash_equilibria(prisoner_dilemma)

    if ne == [('D', 'D')]:
        print(f"  {Color.GREEN}✓{Color.END} 找到纳什均衡: (D, D)")
    else:
        print(f"  {Color.RED}✗{Color.END} 错误: 纳什均衡应该是 [(D, D)]，得到 {ne}")
        return False

    print(f"\n{Color.CYAN}测试 2: 性别战争 (Battle of Sexes){Color.END}")

    # 性别战争：夫妻想一起活动，但偏好不同
    # O = 歌剧, F = 足球
    battle_of_sexes = {
        ('O', 'O'): (2, 1),  # 都去歌剧：丈夫最喜欢
        ('O', 'F'): (0, 0),  # 分开活动：都不开心
        ('F', 'O'): (0, 0),  # 分开活动：都不开心
        ('F', 'F'): (1, 2)   # 都去足球：妻子最喜欢
    }

    ne_bos = find_pure_nash_equilibria(battle_of_sexes)
    ne_bos_set = set(ne_bos)

    if ne_bos_set == {('O', 'O'), ('F', 'F')}:
        print(f"  {Color.GREEN}✓{Color.END} 找到两个纳什均衡: (O, O) 和 (F, F)")
    else:
        print(f"  {Color.RED}✗{Color.END} 错误: 应该找到 (O, O) 和 (F, F)，得到 {ne_bos}")
        return False

    print(f"\n{Color.CYAN}测试 3: 最佳响应{Color.END}")

    # 测试最佳响应函数
    is_br = is_best_response(prisoner_dilemma, 1, 'D', 'D')
    is_not_br = is_best_response(prisoner_dilemma, 1, 'C', 'D')

    if is_br and not is_not_br:
        print(f"  {Color.GREEN}✓{Color.END} 最佳响应判断正确")
    else:
        print(f"  {Color.RED}✗{Color.END} 最佳响应判断错误")
        return False

    print(f"\n{Color.CYAN}测试 4: 获取所有最佳响应{Color.END}")

    brs = get_best_responses(battle_of_sexes, 1, 'O')

    if set(brs) == {'O'}:
        print(f"  {Color.GREEN}✓{Color.END} 正确找到最佳响应")
    else:
        print(f"  {Color.RED}✗{Color.END} 最佳响应错误，期望 ['O']，得到 {brs}")
        return False

    return True


if __name__ == '__main__':
    test()
