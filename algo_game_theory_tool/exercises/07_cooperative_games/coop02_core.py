"""
练习 18: 核心 (The Core)

核心是协同博弈论中的重要解概念，由 Gillies (1959) 提出。

定义：分配方案 x 在核心中，如果：
1. 效率：Σ x_i = v(N) （分配总和等于大联盟价值）
2. 稳定性：对任何联盟 S，Σ_{i∈S} x_i ≥ v(S)
   （联盟成员的总分配 ≥ 该联盟单独行动能获得的价值）

直觉：核心中的分配是"稳定"的，没有联盟有动机脱离大联盟。

性质：
- 核心可能为空（不存在稳定分配）
- 核心可能包含多个分配
- 夏普利值不一定在核心中
- 核心总是凸集

与市场的关系：
核心对应竞争均衡（Edgeworth, 1881）

任务：实现核心的计算和验证。
"""

from itertools import combinations


def is_in_core(allocation, characteristic_function, players):
    """
    检查分配是否在核心中

    参数:
        allocation: 分配方案 {player: value}
        characteristic_function: 特征函数 {frozenset: value}
        players: 所有玩家列表

    返回:
        tuple: (is_in_core, blocking_coalition)
               blocking_coalition: 如果不在核心，返回阻塞联盟
    """
    # TODO: 检查核心条件
    # 1. 检查效率：Σ x_i = v(N)
    # 2. 检查稳定性：对所有联盟 S，Σ_{i∈S} x_i ≥ v(S)
    # 如果存在联盟 S 使得 Σ_{i∈S} x_i < v(S)，
    # 则该联盟是"阻塞联盟"
    pass


def find_core_allocations(characteristic_function, players, grid_size=10):
    """
    尝试找到核心中的分配（通过网格搜索）

    注意：这是一个简化版本，只对小规模博弈有效

    参数:
        characteristic_function: 特征函数
        players: 玩家列表
        grid_size: 搜索网格大小

    返回:
        list: 核心中的分配列表
    """
    # TODO: 搜索核心分配
    # 1. 生成满足效率条件的候选分配
    # 2. 对每个候选，检查是否在核心中
    # 3. 返回所有在核心中的分配
    pass


def compute_core_constraints(characteristic_function, players):
    """
    计算核心的约束条件（线性不等式系统）

    核心可以表示为线性规划的可行域：
    - Σ x_i = v(N)  （等式约束）
    - Σ_{i∈S} x_i ≥ v(S) for all S ⊆ N  （不等式约束）

    参数:
        characteristic_function: 特征函数
        players: 玩家列表

    返回:
        dict: {'equalities': [...], 'inequalities': [...]}
    """
    # TODO: 生成约束条件
    # 对每个联盟，生成一个不等式
    pass


def is_core_nonempty_3player(characteristic_function, players):
    """
    检查3人博弈的核心是否非空（使用 Bondareva-Shapley 定理的简化版本）

    对于3人博弈，核心非空的充要条件：
    v({i,j}) + v({j,k}) + v({i,k}) ≤ 2*v(N) for all i,j,k

    参数:
        characteristic_function: 特征函数
        players: 3个玩家的列表

    返回:
        bool: 核心是否非空
    """
    # TODO: 检查3人博弈核心非空条件
    pass


def shapley_in_core(shapley_values, characteristic_function, players):
    """
    检查夏普利值是否在核心中

    注意：夏普利值不一定在核心中！

    参数:
        shapley_values: 夏普利值 {player: value}
        characteristic_function: 特征函数
        players: 玩家列表

    返回:
        bool: 夏普利值是否在核心中
    """
    # TODO: 检查夏普利值是否在核心中
    pass


# HINT: 核心 = {x : Σx_i = v(N), Σ_{i∈S}x_i ≥ v(S) for all S}
# HINT: 阻塞联盟：Σ_{i∈S}x_i < v(S) 的联盟 S
# HINT: 核心可能为空！这意味着没有稳定的分配
# HINT: 3人博弈：核心非空 iff 三条边不等式成立


def test():
    """测试函数"""
    from exercise_runner import Color

    print(f"{Color.CYAN}测试 1: 简单的3人博弈{Color.END}")

    # 博弈：三个人需要合作才有价值
    # 两人合作价值为6，三人合作价值为9
    players = ['A', 'B', 'C']

    v = {
        frozenset(): 0,
        frozenset(['A']): 0,
        frozenset(['B']): 0,
        frozenset(['C']): 0,
        frozenset(['A', 'B']): 6,
        frozenset(['A', 'C']): 6,
        frozenset(['B', 'C']): 6,
        frozenset(['A', 'B', 'C']): 9
    }

    print(f"  {Color.GREEN}✓{Color.END} 博弈设置：")
    print(f"    两人联盟价值: 6")
    print(f"    大联盟价值: 9")

    print(f"\n{Color.CYAN}测试 2: 检查分配是否在核心中{Color.END}")

    # 平均分配：每人3
    allocation1 = {'A': 3, 'B': 3, 'C': 3}

    is_core, blocking = is_in_core(allocation1, v, players)

    if is_core:
        print(f"  {Color.GREEN}✓{Color.END} (3, 3, 3) 在核心中")
    else:
        print(f"  {Color.RED}✗{Color.END} (3, 3, 3) 应该在核心中")
        print(f"    阻塞联盟: {blocking}")
        return False

    # 验证：
    # v({A,B}) = 6 ≤ x_A + x_B = 6 ✓
    # v({A,C}) = 6 ≤ x_A + x_C = 6 ✓
    # v({B,C}) = 6 ≤ x_B + x_C = 6 ✓

    print(f"\n{Color.CYAN}测试 3: 不在核心中的分配{Color.END}")

    # 不公平分配：A 得太多
    allocation2 = {'A': 5, 'B': 2, 'C': 2}

    is_core2, blocking2 = is_in_core(allocation2, v, players)

    if not is_core2:
        print(f"  {Color.GREEN}✓{Color.END} (5, 2, 2) 不在核心中")
        print(f"    阻塞联盟: {blocking2}")
        print(f"    {Color.YELLOW}B 和 C 可以脱离，获得 v({{B,C}})=6 > 2+2=4{Color.END}")
    else:
        print(f"  {Color.RED}✗{Color.END} (5, 2, 2) 不应该在核心中")
        return False

    print(f"\n{Color.CYAN}测试 4: 核心为空的例子{Color.END}")

    # 经典例子：3人多数投票博弈
    # 任何两人联盟都能决定结果（价值1）
    # 三人联盟价值还是1
    players_voting = ['A', 'B', 'C']

    v_voting = {
        frozenset(): 0,
        frozenset(['A']): 0,
        frozenset(['B']): 0,
        frozenset(['C']): 0,
        frozenset(['A', 'B']): 1,
        frozenset(['A', 'C']): 1,
        frozenset(['B', 'C']): 1,
        frozenset(['A', 'B', 'C']): 1
    }

    print(f"  {Color.YELLOW}3人多数投票博弈：{Color.END}")
    print(f"    两人联盟价值: 1")
    print(f"    大联盟价值: 1")
    print(f"    ")
    print(f"    核心条件：")
    print(f"      x_A + x_B + x_C = 1 (效率)")
    print(f"      x_A + x_B ≥ 1")
    print(f"      x_A + x_C ≥ 1")
    print(f"      x_B + x_C ≥ 1")
    print(f"    ")
    print(f"    相加：2(x_A + x_B + x_C) ≥ 3")
    print(f"    即：x_A + x_B + x_C ≥ 1.5")
    print(f"    ")
    print(f"    但效率要求 x_A + x_B + x_C = 1")
    print(f"    矛盾！{Color.RED}核心为空{Color.END}")

    # 验证核心为空
    is_empty = is_core_nonempty_3player(v_voting, players_voting)

    if not is_empty:
        print(f"  {Color.GREEN}✓{Color.END} 正确判断核心为空")
    else:
        print(f"  {Color.YELLOW}⚠{Color.END} 核心应该为空")

    print(f"\n{Color.CYAN}测试 5: 夏普利值与核心{Color.END}")

    # 对第一个博弈，计算夏普利值
    # 由对称性，夏普利值 = (3, 3, 3)

    shapley = {'A': 3, 'B': 3, 'C': 3}

    shapley_core = shapley_in_core(shapley, v, players)

    if shapley_core:
        print(f"  {Color.GREEN}✓{Color.END} 在这个博弈中，夏普利值在核心中")
        print(f"    夏普利值: (3, 3, 3)")
    else:
        print(f"  {Color.RED}✗{Color.END} 夏普利值应该在核心中")
        return False

    print(f"\n{Color.CYAN}测试 6: 核心与竞争均衡{Color.END}")

    print(f"  {Color.YELLOW}Edgeworth (1881) 等价定理：{Color.END}")
    print(f"    在交换经济中：")
    print(f"    核心中的分配 = 竞争均衡分配")
    print(f"    （当参与者数量 → ∞）")
    print(f"    ")
    print(f"    这连接了博弈论和经济学！")

    print(f"\n{Color.CYAN}测试 7: Bondareva-Shapley 定理{Color.END}")

    print(f"  {Color.YELLOW}定理（Bondareva 1963, Shapley 1967）：{Color.END}")
    print(f"    核心非空 ⟺ 博弈是平衡的 (balanced)")
    print(f"    ")
    print(f"    平衡条件：对所有"平衡权重"λ，")
    print(f"    Σ_S λ_S * v(S) ≤ v(N)")
    print(f"    ")
    print(f"    这给出了核心非空的充要条件！")

    print(f"\n{Color.YELLOW}💡 核心的重要性：{Color.END}")
    print(f"{Color.YELLOW}   - 刻画稳定的分配方案{Color.END}")
    print(f"{Color.YELLOW}   - 连接博弈论与经济学（竞争均衡）{Color.END}")
    print(f"{Color.YELLOW}   - 核心可能为空（无稳定分配）{Color.END}")
    print(f"{Color.YELLOW}   - 应用：成本分摊、联盟形成、市场设计{Color.END}")

    return True


if __name__ == '__main__':
    test()
