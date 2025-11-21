"""
练习 19: 相关均衡 (Correlated Equilibrium)

相关均衡由 Aumann (1974) 提出，是纳什均衡的推广。

核心思想：存在一个"协调装置"发送公开信号，玩家根据信号选择策略。

定义：概率分布 π 在策略组合 S 上是相关均衡，如果对每个玩家 i 和策略 s_i, s_i'：

$$\\sum_{s_{-i}} \\pi(s_i, s_{-i}) [u_i(s_i, s_{-i}) - u_i(s_i', s_{-i})] \\geq 0$$

直觉：当装置建议玩家 i 选择 s_i 时，i 没有动机偏离到 s_i'。

性质：
1. 每个纳什均衡都是相关均衡
2. 相关均衡的集合是凸集
3. 可以在多项式时间内计算（线性规划）
4. 可能比所有纳什均衡的社会福利都更好！

经典例子：交通灯协调

任务：实现相关均衡的验证和计算。
"""

import numpy as np


def is_correlated_equilibrium(distribution, payoff_matrix):
    """
    检查给定的概率分布是否是相关均衡

    参数:
        distribution: 策略组合上的概率分布
                     格式: {(s1, s2): probability}
        payoff_matrix: 支付矩阵 {(s1, s2): (u1, u2)}

    返回:
        bool: 是否是相关均衡
    """
    # TODO: 检查相关均衡条件
    # 对每个玩家 i，每对策略 (s_i, s_i')：
    # Σ_{s_{-i}} π(s_i, s_{-i}) * [u_i(s_i, s_{-i}) - u_i(s_i', s_{-i})] ≥ 0
    pass


def nash_to_correlated(nash_strategy_profile, payoff_matrix):
    """
    将纳什均衡转换为相关均衡

    纳什均衡是特殊的相关均衡（独立分布）

    参数:
        nash_strategy_profile: 纳什均衡（可以是纯策略或混合策略）
        payoff_matrix: 支付矩阵

    返回:
        dict: 相关均衡分布
    """
    # TODO: 将纳什均衡转换为相关均衡
    # 对于纯策略纳什均衡 (s1*, s2*)：
    # π(s1*, s2*) = 1, 其他为 0
    pass


def compute_expected_welfare_correlated(distribution, payoff_matrix):
    """
    计算相关均衡下的期望社会福利

    参数:
        distribution: 相关均衡分布
        payoff_matrix: 支付矩阵

    返回:
        float: 期望社会福利
    """
    # TODO: 计算期望社会福利
    # E[SW] = Σ_s π(s) * (u1(s) + u2(s))
    pass


def find_optimal_correlated_equilibrium(payoff_matrix):
    """
    找到社会福利最大的相关均衡（线性规划）

    这是一个线性规划问题：
    max Σ_s π(s) * SW(s)
    s.t.
      - π(s) ≥ 0 for all s
      - Σ_s π(s) = 1
      - 相关均衡约束（对每个玩家，每对策略）

    参数:
        payoff_matrix: 支付矩阵

    返回:
        dict: 最优相关均衡分布
    """
    # TODO: 使用线性规划找最优相关均衡
    # 这是一个挑战性练习！
    # 可以使用 scipy.optimize.linprog
    pass


def traffic_light_example():
    """
    经典的交通灯例子

    两辆车在十字路口：
    - 如果都走，会撞车（效用 -10）
    - 如果一个走一个停，走的获得 1，停的获得 0
    - 如果都停，都获得 0

    相关均衡：交通灯随机显示"车1走"或"车2走"
    """
    # 支付矩阵
    payoff = {
        ('Go', 'Go'): (-10, -10),
        ('Go', 'Stop'): (1, 0),
        ('Stop', 'Go'): (0, 1),
        ('Stop', 'Stop'): (0, 0)
    }

    # 相关均衡：50% 显示 (Go, Stop), 50% 显示 (Stop, Go)
    correlated_dist = {
        ('Go', 'Go'): 0,
        ('Go', 'Stop'): 0.5,
        ('Stop', 'Go'): 0.5,
        ('Stop', 'Stop'): 0
    }

    return payoff, correlated_dist


# HINT: 相关均衡允许玩家的策略相关（不独立）
# HINT: 纳什均衡 = 独立的相关均衡
# HINT: 相关均衡可以通过线性规划高效计算
# HINT: 可能比所有纳什均衡都更好！


def test():
    """测试函数"""
    from exercise_runner import Color

    print(f"{Color.CYAN}测试 1: 交通灯例子{Color.END}")

    payoff, correlated_dist = traffic_light_example()

    print(f"  {Color.YELLOW}博弈设置：{Color.END}")
    print(f"    两辆车在十字路口")
    print(f"    都走: (-10, -10) - 撞车！")
    print(f"    一走一停: (1, 0) 或 (0, 1)")
    print(f"    都停: (0, 0)")

    is_ce = is_correlated_equilibrium(correlated_dist, payoff)

    if is_ce:
        print(f"  {Color.GREEN}✓{Color.END} 交通灯方案是相关均衡")
        print(f"    分布: 50% (Go,Stop) + 50% (Stop,Go)")
    else:
        print(f"  {Color.RED}✗{Color.END} 交通灯方案应该是相关均衡")
        return False

    print(f"\n{Color.CYAN}测试 2: 计算期望社会福利{Color.END}")

    welfare_ce = compute_expected_welfare_correlated(correlated_dist, payoff)

    # E[SW] = 0.5 * (1+0) + 0.5 * (0+1) = 1
    expected_welfare = 1.0

    if abs(welfare_ce - expected_welfare) < 0.001:
        print(f"  {Color.GREEN}✓{Color.END} 相关均衡的期望社会福利: {welfare_ce}")
    else:
        print(f"  {Color.RED}✗{Color.END} 社会福利计算错误")
        return False

    print(f"\n{Color.CYAN}测试 3: 纳什均衡 vs 相关均衡{Color.END}")

    # 纯策略纳什均衡：(Go, Stop) 和 (Stop, Go)
    # 每个的社会福利都是 1

    # 混合策略纳什均衡：各50%概率Go/Stop（独立）
    nash_mixed = {
        ('Go', 'Go'): 0.25,
        ('Go', 'Stop'): 0.25,
        ('Stop', 'Go'): 0.25,
        ('Stop', 'Stop'): 0.25
    }

    welfare_nash_mixed = compute_expected_welfare_correlated(nash_mixed, payoff)

    # E[SW] = 0.25*(-20) + 0.25*1 + 0.25*1 + 0.25*0 = -4.5

    print(f"  {Color.YELLOW}比较：{Color.END}")
    print(f"    混合纳什均衡（独立）福利: {welfare_nash_mixed:.2f}")
    print(f"    相关均衡（交通灯）福利: {welfare_ce:.2f}")
    print(f"    ")
    print(f"    {Color.GREEN}相关均衡比混合纳什均衡好得多！{Color.END}")

    print(f"\n{Color.CYAN}测试 4: 纳什均衡是相关均衡{Color.END}")

    # 纯策略纳什均衡
    nash_pure = {
        ('Go', 'Go'): 0,
        ('Go', 'Stop'): 1,
        ('Stop', 'Go'): 0,
        ('Stop', 'Stop'): 0
    }

    is_ce_nash = is_correlated_equilibrium(nash_pure, payoff)

    if is_ce_nash:
        print(f"  {Color.GREEN}✓{Color.END} 纳什均衡是相关均衡（验证定理）")
    else:
        print(f"  {Color.RED}✗{Color.END} 纳什均衡应该是相关均衡")
        return False

    print(f"\n{Color.CYAN}测试 5: 相关均衡的优势{Color.END}")

    # 鸡博弈 (Chicken Game)
    chicken = {
        ('Swerve', 'Swerve'): (0, 0),
        ('Swerve', 'Straight'): (-1, 1),
        ('Straight', 'Swerve'): (1, -1),
        ('Straight', 'Straight'): (-10, -10)
    }

    # 最优相关均衡：避免 (Straight, Straight)
    # 均匀分布在其他三个结果上
    optimal_ce = {
        ('Swerve', 'Swerve'): 1/3,
        ('Swerve', 'Straight'): 1/3,
        ('Straight', 'Swerve'): 1/3,
        ('Straight', 'Straight'): 0
    }

    welfare_optimal = compute_expected_welfare_correlated(optimal_ce, chicken)

    print(f"  {Color.YELLOW}鸡博弈最优相关均衡：{Color.END}")
    print(f"    避免最坏结果 (Straight, Straight)")
    print(f"    期望社会福利: {welfare_optimal:.2f}")

    print(f"\n{Color.CYAN}测试 6: 线性规划性质{Color.END}")

    print(f"  {Color.YELLOW}计算相关均衡的优势：{Color.END}")
    print(f"    - 纳什均衡: PPAD-complete（难）")
    print(f"    - 相关均衡: 线性规划（多项式时间）")
    print(f"    ")
    print(f"    相关均衡可以高效计算！")

    print(f"\n{Color.CYAN}测试 7: 为什么相关均衡重要？{Color.END}")

    print(f"  {Color.YELLOW}三个原因：{Color.END}")
    print(f"    1. {Color.GREEN}可高效计算{Color.END}（vs 纳什均衡的PPAD-complete）")
    print(f"    2. {Color.GREEN}社会福利更好{Color.END}（可能严格优于所有纳什均衡）")
    print(f"    3. {Color.GREEN}更现实{Color.END}（允许协调装置，如交通灯、推荐系统）")

    print(f"\n{Color.YELLOW}💡 相关均衡的意义：{Color.END}")
    print(f"{Color.YELLOW}   - 推广纳什均衡（包含更多解）{Color.END}")
    print(f"{Color.YELLOW}   - 可高效计算（线性规划）{Color.END}")
    print(f"{Color.YELLOW}   - 允许通过协调提高效率{Color.END}")
    print(f"{Color.YELLOW}   - 应用：交通系统、推荐算法、网络路由{Color.END}")

    return True


if __name__ == '__main__':
    test()
