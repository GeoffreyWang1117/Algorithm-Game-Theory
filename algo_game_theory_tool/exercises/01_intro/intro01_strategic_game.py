"""
练习 1: 策略式博弈 (Strategic Game)

在算法博弈论中，策略式博弈是最基本的博弈模型。一个策略式博弈包括：
1. 玩家集合 (Players)
2. 每个玩家的策略集合 (Strategy Sets)
3. 每个玩家的效用函数 (Utility Functions)

任务：实现一个 StrategicGame 类，能够表示一个两人有限策略博弈。
"""


class StrategicGame:
    """表示一个两人策略式博弈"""

    def __init__(self, player1_strategies, player2_strategies, payoff_matrix):
        """
        初始化博弈

        参数:
            player1_strategies: 玩家1的策略列表
            player2_strategies: 玩家2的策略列表
            payoff_matrix: 支付矩阵，格式为 {(s1, s2): (u1, u2)}
                          其中 s1, s2 是策略，u1, u2 是对应的效用
        """
        # TODO: 实现初始化逻辑
        pass

    def get_payoff(self, strategy1, strategy2):
        """
        获取给定策略组合下两个玩家的效用

        参数:
            strategy1: 玩家1的策略
            strategy2: 玩家2的策略

        返回:
            (u1, u2): 两个玩家的效用元组
        """
        # TODO: 实现获取效用的逻辑
        pass

    def get_player1_strategies(self):
        """返回玩家1的所有策略"""
        # TODO: 实现
        pass

    def get_player2_strategies(self):
        """返回玩家2的所有策略"""
        # TODO: 实现
        pass


# HINT: 策略式博弈的关键是要正确存储策略和对应的效用值
# HINT: 可以用字典来存储 payoff_matrix，键是策略对，值是效用对


def test():
    """测试函数"""
    from exercise_runner import validate_function, Color

    # 创建一个经典的囚徒困境博弈
    # C = 合作 (Cooperate), D = 背叛 (Defect)
    prisoner_dilemma = StrategicGame(
        player1_strategies=['C', 'D'],
        player2_strategies=['C', 'D'],
        payoff_matrix={
            ('C', 'C'): (-1, -1),  # 双方合作：各判1年
            ('C', 'D'): (-3, 0),   # P1合作P2背叛：P1判3年，P2释放
            ('D', 'C'): (0, -3),   # P1背叛P2合作：P1释放，P2判3年
            ('D', 'D'): (-2, -2)   # 双方背叛：各判2年
        }
    )

    print(f"{Color.CYAN}测试 1: 囚徒困境{Color.END}")

    # 测试效用获取
    test_cases = [
        (('C', 'C'), (-1, -1), "双方合作"),
        (('C', 'D'), (-3, 0), "P1合作P2背叛"),
        (('D', 'C'), (0, -3), "P1背叛P2合作"),
        (('D', 'D'), (-2, -2), "双方背叛"),
    ]

    passed = validate_function(prisoner_dilemma.get_payoff, test_cases, "get_payoff")

    # 测试策略获取
    print(f"\n{Color.CYAN}测试 2: 策略集合{Color.END}")
    strategies1 = prisoner_dilemma.get_player1_strategies()
    strategies2 = prisoner_dilemma.get_player2_strategies()

    if set(strategies1) == {'C', 'D'} and set(strategies2) == {'C', 'D'}:
        print(f"  {Color.GREEN}✓{Color.END} 策略集合正确")
    else:
        print(f"  {Color.RED}✗{Color.END} 策略集合不正确")
        passed = False

    return passed


if __name__ == '__main__':
    test()
