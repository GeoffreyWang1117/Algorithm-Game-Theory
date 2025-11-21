"""
练习 15: 自私路由与 Wardrop 均衡 (Selfish Routing & Wardrop Equilibrium)

自私路由是网络博弈的经典问题，由 Wardrop (1952) 提出。
在交通网络或数据网络中，每个用户选择使自己成本最小的路径，
但不考虑对其他用户的影响。

核心概念：
- Wardrop 均衡：没有用户能通过单方面改变路径来降低成本
- 边延迟函数：l_e(x) 表示边 e 上流量为 x 时的延迟
- 社会成本：所有用户总延迟之和

Pigou 例子：
```
    [成本: x]
s ─────────────→ t
    ↓ [成本: 1]
```

流量 r=1 时：
- 自私路由：全部走下路，总成本 = 1
- 社会最优：可能分流更好

定理（Roughgarden-Tardos）：
线性延迟函数时，PoA ≤ 4/3

任务：实现自私路由的计算和效率分析。
"""

from collections import defaultdict


class SelishRoutingNetwork:
    """自私路由网络"""

    def __init__(self):
        """
        初始化网络

        网络表示为：
        - edges: {(u, v): delay_function}
        - delay_function: 延迟函数，输入流量 x，输出延迟
        """
        self.edges = {}  # (u, v) -> delay_function
        self.paths = []  # 可能的路径列表

    def add_edge(self, u, v, delay_function):
        """
        添加边和延迟函数

        参数:
            u, v: 起点终点
            delay_function: 延迟函数 f(x)，x 是边上的流量
        """
        # TODO: 实现添加边
        pass

    def set_paths(self, paths):
        """
        设置所有可能的路径

        参数:
            paths: 路径列表，每个路径是边的列表
        """
        # TODO: 设置路径
        pass


def compute_path_delay(network, path, flow_on_edges):
    """
    计算给定流量分配下某条路径的延迟

    参数:
        network: 网络
        path: 路径（边的列表）
        flow_on_edges: 每条边上的流量 {(u,v): flow}

    返回:
        float: 路径延迟（路径上所有边延迟之和）
    """
    # TODO: 计算路径延迟
    # 路径延迟 = Σ l_e(x_e) for e in path
    pass


def is_wardrop_equilibrium(network, flow_on_paths, total_flow):
    """
    检查是否是 Wardrop 均衡

    Wardrop 均衡条件：
    - 所有被使用的路径有相同的延迟（且是最小的）
    - 未使用的路径延迟 ≥ 被使用路径的延迟

    参数:
        network: 网络
        flow_on_paths: 每条路径上的流量 {path_index: flow}
        total_flow: 总流量

    返回:
        bool: 是否是 Wardrop 均衡
    """
    # TODO: 检查 Wardrop 均衡条件
    pass


def compute_social_cost(network, flow_on_edges):
    """
    计算社会成本（所有用户总延迟）

    社会成本 = Σ_e x_e * l_e(x_e)
    其中 x_e 是边 e 上的流量，l_e(x_e) 是延迟

    参数:
        network: 网络
        flow_on_edges: 边流量分配

    返回:
        float: 社会成本
    """
    # TODO: 计算社会成本
    pass


def find_selfish_routing(network, total_flow, source, target):
    """
    找到自私路由（Wardrop 均衡）

    对于简单网络，可以用以下方法：
    1. 枚举可能的流量分配
    2. 检查 Wardrop 条件

    参数:
        network: 网络
        total_flow: 总流量 r
        source: 源节点
        target: 目标节点

    返回:
        dict: 流量分配 {path: flow}
    """
    # TODO: 计算自私路由
    # 提示：对于两条平行路径，在均衡时两条路径延迟相等
    pass


def compute_price_of_anarchy_routing(network, total_flow):
    """
    计算路由博弈的无政府代价

    PoA = 自私路由的社会成本 / 社会最优成本

    参数:
        network: 网络
        total_flow: 总流量

    返回:
        float: PoA
    """
    # TODO: 计算 PoA
    # 1. 找到自私路由（Wardrop 均衡）
    # 2. 计算其社会成本
    # 3. 找到社会最优（最小化总成本的流量分配）
    # 4. 返回比值
    pass


# HINT: Wardrop 均衡类似于纳什均衡，但是连续的
# HINT: 在均衡时，所有被使用的路径延迟相等
# HINT: 对于线性延迟 l(x) = ax + b，可以解析求解


def test():
    """测试函数"""
    from exercise_runner import Color

    print(f"{Color.CYAN}测试 1: 构建简单网络{Color.END}")

    # 经典的 Pigou 网络
    # 上路：延迟 = x（流量）
    # 下路：延迟 = 1（常数）
    network = SelishRoutingNetwork()

    # 添加两条从 s 到 t 的边
    network.add_edge('s', 't', lambda x: x)      # 上路：l(x) = x
    network.add_edge('s', 't', lambda x: 1)      # 下路：l(x) = 1

    # 两条路径（每条路径只有一条边）
    network.set_paths([
        [('s', 't')],  # 路径1：上路
        [('s', 't')]   # 路径2：下路（注意：这里实际是不同的边）
    ])

    print(f"  {Color.GREEN}✓{Color.END} 网络构建成功")

    print(f"\n{Color.CYAN}测试 2: 路径延迟计算{Color.END}")

    # 假设上路流量 0.5，下路流量 0.5
    flow_on_edges = {
        ('s', 't', 0): 0.5,  # 上路
        ('s', 't', 1): 0.5   # 下路
    }

    # 这个测试需要你完成实现后才能运行
    # delay1 = compute_path_delay(network, [('s', 't', 0)], flow_on_edges)
    # delay2 = compute_path_delay(network, [('s', 't', 1)], flow_on_edges)

    print(f"  {Color.YELLOW}提示：完成实现后测试路径延迟{Color.END}")

    print(f"\n{Color.CYAN}测试 3: Pigou 网络的自私路由{Color.END}")

    # 对于流量 r=1 的 Pigou 网络：
    # 自私路由：全部走下路（延迟=1）
    # 原因：如果上路有流量 x，延迟 = x
    #       如果 x > 0，理性用户会转到下路（延迟=1）
    #       只有当 x=0 时才是均衡

    print(f"  {Color.GREEN}理论分析：{Color.END}")
    print(f"    总流量 r=1 时")
    print(f"    自私路由：全部走下路，每人延迟=1，总成本=1")
    print(f"    社会最优：也是全部走下路，总成本=1")
    print(f"    {Color.YELLOW}这个例子中 PoA = 1{Color.END}")

    print(f"\n{Color.CYAN}测试 4: 更糟糕的 Pigou 网络{Color.END}")

    # 上路：l(x) = x
    # 下路：l(x) = 1
    # 但现在延迟函数改为二次：l(x) = x²

    print(f"  {Color.YELLOW}如果上路延迟是 l(x) = x²:{Color.END}")
    print(f"    自私路由：可能不是全走一条路")
    print(f"    需要求解：找到使两条路延迟相等的分配")

    print(f"\n{Color.CYAN}测试 5: Braess 悖论{Color.END}")

    # Braess 悖论：增加边可能增加总延迟！
    print(f"  {Color.YELLOW}经典例子：{Color.END}")
    print(f"    原网络：")
    print(f"          ──[x]──")
    print(f"        s         t")
    print(f"          ──[x]──")
    print(f"    ")
    print(f"    加一条免费捷径后，均衡延迟反而增加！")
    print(f"    原因：自私的用户都选择捷径，导致拥塞")

    print(f"\n{Color.CYAN}测试 6: 线性延迟的 PoA{Color.END}")

    print(f"  {Color.YELLOW}Roughgarden-Tardos 定理：{Color.END}")
    print(f"    对于线性延迟函数 l(x) = ax + b")
    print(f"    无政府代价 PoA ≤ 4/3")
    print(f"    ")
    print(f"    这意味着：自私路由最多比最优差 33%")

    print(f"\n{Color.YELLOW}💡 自私路由的重要性：{Color.END}")
    print(f"{Color.YELLOW}   - 建模交通拥塞、网络路由{Color.END}")
    print(f"{Color.YELLOW}   - Braess 悖论：增加容量可能使情况更糟{Color.END}")
    print(f"{Color.YELLOW}   - PoA 提供效率保证{Color.END}")
    print(f"{Color.YELLOW}   - 应用：导航系统、CDN、交通规划{Color.END}")

    return True


if __name__ == '__main__':
    test()
