"""
练习 12: 夏普利值 (Shapley Value)

夏普利值是协同博弈论中的经典解概念，由 Lloyd Shapley (1953) 提出，
为此他获得了2012年诺贝尔经济学奖。

核心思想：公平地分配合作带来的总价值，考虑每个玩家的边际贡献。

夏普利值满足四个公理：
1. 效率 (Efficiency)：分配总和等于总价值
2. 对称性 (Symmetry)：贡献相同的玩家获得相同分配
3. 虚拟玩家 (Null Player)：无贡献的玩家获得0
4. 可加性 (Additivity)：两个博弈之和的夏普利值等于各自夏普利值之和

数学定义（对于玩家 i）：
$$\\phi_i(v) = \\sum_{S \\subseteq N \\setminus \\{i\\}} \\frac{|S|!(n-|S|-1)!}{n!} [v(S \\cup \\{i\\}) - v(S)]$$

任务：实现夏普利值的计算。
"""

from itertools import combinations, permutations


def shapley_value(characteristic_function, player):
    """
    计算指定玩家的夏普利值

    参数:
        characteristic_function: 特征函数 v(S)，输入联盟，输出价值
                                格式为 dict {frozenset: value}
        player: 玩家标识

    返回:
        float: 该玩家的夏普利值
    """
    # TODO: 实现夏普利值计算
    # 方法1：使用公式 Σ (|S|!(n-|S|-1)!/n!) * [v(S∪{i}) - v(S)]
    # 方法2：枚举所有排列，计算平均边际贡献
    pass


def shapley_value_by_permutation(characteristic_function, player, players):
    """
    通过排列方法计算夏普利值

    思想：枚举所有玩家到达顺序，计算平均边际贡献

    对于排列 π，玩家 i 的边际贡献 = v(π前面的人∪{i}) - v(π前面的人)
    夏普利值 = 所有排列中边际贡献的平均

    参数:
        characteristic_function: 特征函数
        player: 玩家标识
        players: 所有玩家列表

    返回:
        float: 夏普利值
    """
    # TODO: 实现基于排列的夏普利值计算
    # 1. 枚举所有排列
    # 2. 对每个排列，计算该玩家的边际贡献
    # 3. 返回平均值
    pass


def verify_efficiency(shapley_values, characteristic_function, players):
    """
    验证效率公理：所有玩家的夏普利值之和等于大联盟的价值

    参数:
        shapley_values: 夏普利值字典 {player: value}
        characteristic_function: 特征函数
        players: 所有玩家

    返回:
        bool: 是否满足效率公理
    """
    # TODO: 验证 Σ φ_i = v(N)
    pass


def calculate_all_shapley_values(characteristic_function, players):
    """
    计算所有玩家的夏普利值

    参数:
        characteristic_function: 特征函数
        players: 所有玩家列表

    返回:
        dict: {player: shapley_value}
    """
    # TODO: 计算所有玩家的夏普利值
    pass


# HINT: 夏普利值 = 加权平均的边际贡献
# HINT: 边际贡献 = v(S ∪ {i}) - v(S)
# HINT: 权重 = |S|!(n-|S|-1)!/n!（S 是不包含 i 的联盟）
# HINT: 排列方法更直观：平均每个到达顺序中的边际贡献


def test():
    """测试函数"""
    from exercise_runner import Color

    print(f"{Color.CYAN}测试 1: 简单的三人博弈{Color.END}")

    # 三个玩家：A, B, C
    # 规则：至少两个人合作才能产生价值1，三人合作价值2
    players = ['A', 'B', 'C']

    v = {
        frozenset(): 0,
        frozenset(['A']): 0,
        frozenset(['B']): 0,
        frozenset(['C']): 0,
        frozenset(['A', 'B']): 1,
        frozenset(['A', 'C']): 1,
        frozenset(['B', 'C']): 1,
        frozenset(['A', 'B', 'C']): 2
    }

    # 由对称性，每个玩家应该获得相同的夏普利值
    sv_a = shapley_value(v, 'A')
    sv_b = shapley_value(v, 'B')
    sv_c = shapley_value(v, 'C')

    expected_value = 2 / 3  # 每人应得 2/3

    if (abs(sv_a - expected_value) < 0.001 and
        abs(sv_b - expected_value) < 0.001 and
        abs(sv_c - expected_value) < 0.001):
        print(f"  {Color.GREEN}✓{Color.END} 夏普利值计算正确（对称性）")
        print(f"    φ(A) = φ(B) = φ(C) = {sv_a:.3f}")
    else:
        print(f"  {Color.RED}✗{Color.END} 夏普利值错误")
        print(f"    期望: {expected_value:.3f}")
        print(f"    实际: A={sv_a:.3f}, B={sv_b:.3f}, C={sv_c:.3f}")
        return False

    print(f"\n{Color.CYAN}测试 2: 验证效率公理{Color.END}")

    shapley_values = calculate_all_shapley_values(v, players)
    is_efficient = verify_efficiency(shapley_values, v, players)

    if is_efficient:
        total = sum(shapley_values.values())
        grand_coalition_value = v[frozenset(players)]
        print(f"  {Color.GREEN}✓{Color.END} 满足效率公理")
        print(f"    总分配: {total:.3f}")
        print(f"    大联盟价值: {grand_coalition_value}")
    else:
        print(f"  {Color.RED}✗{Color.END} 不满足效率公理")
        return False

    print(f"\n{Color.CYAN}测试 3: 不对称博弈（大玩家和小玩家）{Color.END}")

    # 玩家A是"大玩家"：A和任何人合作都能产生价值10
    # 玩家B、C是"小玩家"：单独或互相合作都无价值
    players2 = ['A', 'B', 'C']

    v2 = {
        frozenset(): 0,
        frozenset(['A']): 0,
        frozenset(['B']): 0,
        frozenset(['C']): 0,
        frozenset(['A', 'B']): 10,
        frozenset(['A', 'C']): 10,
        frozenset(['B', 'C']): 0,
        frozenset(['A', 'B', 'C']): 10
    }

    sv2_a = shapley_value(v2, 'A')
    sv2_b = shapley_value(v2, 'B')
    sv2_c = shapley_value(v2, 'C')

    # A是关键玩家，应该获得大部分价值
    # 可以计算：φ(A) = 10 * 2/3 = 6.67, φ(B) = φ(C) = 10/6 = 1.67

    if sv2_a > sv2_b and abs(sv2_b - sv2_c) < 0.001:
        print(f"  {Color.GREEN}✓{Color.END} 正确识别大玩家和小玩家")
        print(f"    φ(A) = {sv2_a:.3f} (大玩家)")
        print(f"    φ(B) = {sv2_b:.3f} (小玩家)")
        print(f"    φ(C) = {sv2_c:.3f} (小玩家)")
    else:
        print(f"  {Color.RED}✗{Color.END} 分配不合理")
        return False

    print(f"\n{Color.CYAN}测试 4: 虚拟玩家{Color.END}")

    # 玩家D是虚拟玩家（无论加入哪个联盟都不增加价值）
    players3 = ['A', 'B', 'D']

    v3 = {
        frozenset(): 0,
        frozenset(['A']): 0,
        frozenset(['B']): 0,
        frozenset(['D']): 0,
        frozenset(['A', 'B']): 10,
        frozenset(['A', 'D']): 0,
        frozenset(['B', 'D']): 0,
        frozenset(['A', 'B', 'D']): 10
    }

    sv3_d = shapley_value(v3, 'D')

    if abs(sv3_d) < 0.001:
        print(f"  {Color.GREEN}✓{Color.END} 虚拟玩家获得0")
        print(f"    φ(D) = {sv3_d:.3f}")
    else:
        print(f"  {Color.RED}✗{Color.END} 虚拟玩家应该获得0")
        print(f"    实际: φ(D) = {sv3_d:.3f}")
        return False

    print(f"\n{Color.CYAN}测试 5: 排列方法验证{Color.END}")

    # 验证两种计算方法得到相同结果
    sv_perm_a = shapley_value_by_permutation(v, 'A', players)

    if abs(sv_perm_a - sv_a) < 0.001:
        print(f"  {Color.GREEN}✓{Color.END} 排列方法与公式方法一致")
        print(f"    公式方法: {sv_a:.3f}")
        print(f"    排列方法: {sv_perm_a:.3f}")
    else:
        print(f"  {Color.RED}✗{Color.END} 两种方法结果不一致")
        return False

    print(f"\n{Color.YELLOW}💡 夏普利值的意义：{Color.END}")
    print(f"{Color.YELLOW}   - 唯一满足四个公理的分配方案{Color.END}")
    print(f"{Color.YELLOW}   - 考虑了每个玩家的边际贡献{Color.END}")
    print(f"{Color.YELLOW}   - 广泛应用于成本分摊、归因分析等{Color.END}")

    return True


if __name__ == '__main__':
    test()
