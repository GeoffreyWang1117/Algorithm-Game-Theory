"""
练习 14: 势函数博弈 (Potential Games)

势函数博弈由 Monderer 和 Shapley (1996) 提出，是一类具有良好性质的博弈。

核心思想：存在一个"势函数" Φ，使得每个玩家改变策略时，
势函数的变化等于该玩家效用的变化。

定义：博弈 G 是精确势博弈 (Exact Potential Game)，如果存在函数 Φ: S → ℝ，
使得对所有玩家 i，所有 s_{-i}，所有 s_i, s_i'：

$$\\Phi(s_i', s_{-i}) - \\Phi(s_i, s_{-i}) = u_i(s_i', s_{-i}) - u_i(s_i, s_{-i})$$

关键性质：
1. 纯策略纳什均衡存在：势函数的最大值点是纳什均衡
2. 最佳响应动态收敛：有限步骤内收敛到纳什均衡
3. 拥塞博弈都是势博弈

任务：识别势博弈并计算势函数。
"""


def is_potential_game(payoff_matrix):
    """
    判断一个二人博弈是否是势博弈

    参数:
        payoff_matrix: 支付矩阵 {(s1, s2): (u1, u2)}

    返回:
        bool: 是否是势博弈
    """
    # TODO: 判断是否存在势函数
    # 提示：检查改善路径是否满足守恒条件（无循环改善）
    # 或者尝试构造势函数并验证
    pass


def compute_potential_function(payoff_matrix):
    """
    计算势函数（如果存在）

    参数:
        payoff_matrix: 支付矩阵

    返回:
        dict: 势函数 {(s1, s2): potential_value}，如果不是势博弈返回 None
    """
    # TODO: 构造势函数
    # 方法：从某个参考点开始，通过边际效用变化构造势函数
    # 1. 选择参考策略，设 Φ = 0
    # 2. 通过单个玩家改变策略，累积效用变化
    # 3. 验证构造的函数满足势函数性质
    pass


def find_potential_maximizer(potential_function):
    """
    找出势函数的最大值点（这些是纳什均衡）

    参数:
        potential_function: 势函数 {(s1, s2): value}

    返回:
        list: 最大值点列表（纳什均衡）
    """
    # TODO: 找出势函数的最大值点
    pass


def best_response_dynamics(payoff_matrix, initial_strategy, max_iterations=100):
    """
    运行最佳响应动态（Best Response Dynamics）

    在势博弈中，BRD 保证收敛到纳什均衡

    参数:
        payoff_matrix: 支付矩阵
        initial_strategy: 初始策略组合
        max_iterations: 最大迭代次数

    返回:
        tuple: (final_strategy, path, converged)
               path: 策略序列
               converged: 是否收敛到纳什均衡
    """
    # TODO: 实现最佳响应动态
    # 1. 从初始策略开始
    # 2. 每轮随机选择一个玩家
    # 3. 该玩家移动到最佳响应
    # 4. 如果达到纳什均衡则停止
    # 5. 返回路径和结果
    pass


def verify_improvement_path_acyclicity(payoff_matrix):
    """
    验证改善路径无环性（势博弈的必要条件）

    如果博弈是势博弈，则不存在循环改善路径

    参数:
        payoff_matrix: 支付矩阵

    返回:
        bool: 是否满足无环性
    """
    # TODO: 检查是否存在循环改善路径
    # 改善路径：每步都有某个玩家严格改善其效用
    pass


# HINT: 势博弈的判定：
#       尝试构造势函数，验证 Φ(s'_i, s_{-i}) - Φ(s_i, s_{-i}) = u_i(s'_i, s_{-i}) - u_i(s_i, s_{-i})
# HINT: 构造方法：从参考点开始，沿着玩家移动累积效用变化
# HINT: 势函数的最大值点是纳什均衡


def test():
    """测试函数"""
    from exercise_runner import Color

    print(f"{Color.CYAN}测试 1: 协调博弈（是势博弈）{Color.END}")

    # 协调博弈是经典的势博弈例子
    coordination_game = {
        ('A', 'A'): (10, 10),
        ('A', 'B'): (0, 0),
        ('B', 'A'): (0, 0),
        ('B', 'B'): (5, 5)
    }

    is_potential = is_potential_game(coordination_game)

    if is_potential:
        print(f"  {Color.GREEN}✓{Color.END} 正确识别为势博弈")
    else:
        print(f"  {Color.RED}✗{Color.END} 协调博弈应该是势博弈")
        return False

    print(f"\n{Color.CYAN}测试 2: 计算势函数{Color.END}")

    potential = compute_potential_function(coordination_game)

    if potential is not None:
        print(f"  {Color.GREEN}✓{Color.END} 成功计算势函数:")
        for strategy, value in sorted(potential.items()):
            print(f"    Φ{strategy} = {value}")
    else:
        print(f"  {Color.RED}✗{Color.END} 应该能计算势函数")
        return False

    print(f"\n{Color.CYAN}测试 3: 势函数最大值点是纳什均衡{Color.END}")

    maximizers = find_potential_maximizer(potential)

    # (A, A) 应该是势函数最大值点（也是最优纳什均衡）
    if ('A', 'A') in maximizers:
        print(f"  {Color.GREEN}✓{Color.END} 势函数最大值点: {maximizers}")
        print(f"  {Color.YELLOW}💡 这些都是纳什均衡！{Color.END}")
    else:
        print(f"  {Color.RED}✗{Color.END} (A, A) 应该是最大值点")
        return False

    print(f"\n{Color.CYAN}测试 4: 最佳响应动态收敛{Color.END}")

    # 从次优均衡 (B, B) 开始
    final, path, converged = best_response_dynamics(
        coordination_game,
        ('B', 'B'),
        max_iterations=10
    )

    if converged:
        print(f"  {Color.GREEN}✓{Color.END} BRD 收敛到纳什均衡: {final}")
        print(f"    路径长度: {len(path)}")
    else:
        print(f"  {Color.YELLOW}⚠{Color.END} BRD 在势博弈中应该收敛")
        # 不算失败，因为可能陷入局部均衡

    print(f"\n{Color.CYAN}测试 5: 匹配硬币（不是势博弈）{Color.END}")

    # 匹配硬币有循环改善路径，不是势博弈
    matching_pennies = {
        ('H', 'H'): (1, -1),
        ('H', 'T'): (-1, 1),
        ('T', 'H'): (-1, 1),
        ('T', 'T'): (1, -1)
    }

    is_potential_mp = is_potential_game(matching_pennies)

    if not is_potential_mp:
        print(f"  {Color.GREEN}✓{Color.END} 正确识别匹配硬币不是势博弈")
        print(f"  {Color.YELLOW}💡 匹配硬币有循环改善路径{Color.END}")
    else:
        print(f"  {Color.RED}✗{Color.END} 匹配硬币不应该是势博弈")
        return False

    print(f"\n{Color.CYAN}测试 6: 囚徒困境（是势博弈）{Color.END}")

    prisoner_dilemma = {
        ('C', 'C'): (-1, -1),
        ('C', 'D'): (-3, 0),
        ('D', 'C'): (0, -3),
        ('D', 'D'): (-2, -2)
    }

    is_potential_pd = is_potential_game(prisoner_dilemma)
    potential_pd = compute_potential_function(prisoner_dilemma) if is_potential_pd else None

    if is_potential_pd and potential_pd:
        print(f"  {Color.GREEN}✓{Color.END} 囚徒困境是势博弈")

        # 势函数最大值点应该是 (D, D)
        max_pd = find_potential_maximizer(potential_pd)
        if ('D', 'D') in max_pd:
            print(f"  {Color.GREEN}✓{Color.END} 势函数最大值点是 (D, D)")
            print(f"  {Color.YELLOW}💡 注意：(D, D) 是纳什均衡但不是社会最优{Color.END}")
        else:
            print(f"  {Color.RED}✗{Color.END} 最大值点错误")
            return False
    else:
        print(f"  {Color.YELLOW}⚠{Color.END} 囚徒困境应该是势博弈")

    print(f"\n{Color.YELLOW}💡 势博弈的重要性：{Color.END}")
    print(f"{Color.YELLOW}   - 保证纯策略纳什均衡存在{Color.END}")
    print(f"{Color.YELLOW}   - 最佳响应动态保证收敛{Color.END}")
    print(f"{Color.YELLOW}   - 所有拥塞博弈都是势博弈{Color.END}")
    print(f"{Color.YELLOW}   - 应用：网络路由、资源分配等{Color.END}")

    return True


if __name__ == '__main__':
    test()
