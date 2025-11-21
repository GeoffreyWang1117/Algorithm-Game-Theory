"""
练习 17: 投票规则与策略投票 (Voting Rules & Strategic Voting)

投票理论是社会选择理论的核心，研究如何从个人偏好聚合出社会选择。

常见投票规则：
1. 多数规则 (Plurality): 得票最多者获胜
2. Borda 计数: 排名第一得 n-1 分，第二得 n-2 分...
3. 逐对比较 (Condorcet): 一对一比较
4. 即时径流 (Instant Runoff): 逐轮淘汰最少票者

策略投票：
投票者不诚实报告偏好以获得更好结果的行为。

Gibbard-Satterthwaite 定理：
对于 ≥3 个候选人，任何非独裁的投票规则都可能被策略操纵。

任务：实现多种投票规则并分析策略投票。
"""


def plurality_voting(votes):
    """
    多数规则投票（得票最多者获胜）

    参数:
        votes: 投票列表，每个投票是候选人的偏好排序
               例如: [['A', 'B', 'C'], ['B', 'A', 'C'], ...]
               每个列表的第一个元素是该投票者的首选

    返回:
        str: 获胜者
    """
    # TODO: 实现多数规则
    # 统计每个候选人作为首选的次数
    # 返回首选票数最多的候选人
    pass


def borda_count(votes):
    """
    Borda 计数投票

    每个候选人获得的分数：
    - 排名第1: n-1 分
    - 排名第2: n-2 分
    - ...
    - 排名第n: 0 分

    参数:
        votes: 投票列表（偏好排序）

    返回:
        str: 获胜者（总分最高）
    """
    # TODO: 实现 Borda 计数
    pass


def condorcet_winner(votes):
    """
    找Condorcet获胜者

    Condorcet 获胜者：在一对一比较中击败所有其他候选人

    注意：Condorcet 获胜者可能不存在（Condorcet 悖论）

    参数:
        votes: 投票列表

    返回:
        str or None: Condorcet 获胜者，如果不存在返回 None
    """
    # TODO: 实现 Condorcet 获胜者
    # 1. 提取所有候选人
    # 2. 对每对候选人 (a, b)，统计偏好 a over b 的投票数
    # 3. 如果某候选人击败所有其他人，返回该候选人
    pass


def pairwise_comparison(votes, candidate_a, candidate_b):
    """
    一对一比较：统计偏好 a over b 的投票数

    参数:
        votes: 投票列表
        candidate_a, candidate_b: 两个候选人

    返回:
        int: 偏好 a over b 的投票数
    """
    # TODO: 实现一对一比较
    # 对每张选票，检查 a 是否排在 b 前面
    pass


def is_strategyproof(voting_rule, votes, manipulator, true_preference,
                     strategic_vote):
    """
    检查某个投票者是否能通过策略投票获益

    参数:
        voting_rule: 投票规则函数
        votes: 其他人的真实投票
        manipulator: 操纵者的索引
        true_preference: 操纵者的真实偏好
        strategic_vote: 操纵者的策略投票

    返回:
        bool: 策略投票是否使操纵者获益
    """
    # TODO: 检查策略投票是否有效
    # 1. 计算诚实投票下的获胜者
    # 2. 计算策略投票下的获胜者
    # 3. 根据真实偏好比较两个获胜者
    pass


def find_strategic_vote(voting_rule, votes, manipulator, true_preference,
                       candidates):
    """
    尝试找到有益的策略投票

    参数:
        voting_rule: 投票规则
        votes: 其他人的投票
        manipulator: 操纵者
        true_preference: 真实偏好
        candidates: 所有候选人

    返回:
        list or None: 有益的策略投票，如果不存在返回 None
    """
    # TODO: 搜索有益的策略投票
    # 可以枚举所有可能的投票排序
    # 这是一个挑战性练习！
    pass


# HINT: 多数规则：只看第一选择
# HINT: Borda 计数：考虑完整排序
# HINT: Condorcet：可能存在循环（A>B>C>A）
# HINT: 策略投票：谎报偏好可能导致更好的结果


def test():
    """测试函数"""
    from exercise_runner import Color

    print(f"{Color.CYAN}测试 1: 多数规则投票{Color.END}")

    votes1 = [
        ['A', 'B', 'C'],  # 投票者1最喜欢A
        ['A', 'C', 'B'],  # 投票者2最喜欢A
        ['B', 'C', 'A'],  # 投票者3最喜欢B
        ['C', 'B', 'A']   # 投票者4最喜欢C
    ]

    winner_plurality = plurality_voting(votes1)

    if winner_plurality == 'A':
        print(f"  {Color.GREEN}✓{Color.END} 多数规则获胜者: A (2票)")
    else:
        print(f"  {Color.RED}✗{Color.END} 多数规则错误")
        return False

    print(f"\n{Color.CYAN}测试 2: Borda 计数{Color.END}")

    # 同样的投票
    # A: (2*2 + 1*1 + 1*0) = 5分
    # B: (2*1 + 1*2 + 1*1) = 5分
    # C: (2*0 + 1*1 + 1*2) = 4分

    winner_borda = borda_count(votes1)

    print(f"  {Color.GREEN}✓{Color.END} Borda 计数获胜者: {winner_borda}")
    print(f"    {Color.YELLOW}注意：Borda 可能与多数规则不同{Color.END}")

    print(f"\n{Color.CYAN}测试 3: Condorcet 获胜者{Color.END}")

    # Condorcet 获胜者存在的例子
    votes2 = [
        ['A', 'B', 'C'],
        ['A', 'B', 'C'],
        ['A', 'B', 'C'],
        ['B', 'C', 'A']
    ]

    condorcet_win = condorcet_winner(votes2)

    if condorcet_win == 'A':
        print(f"  {Color.GREEN}✓{Color.END} Condorcet 获胜者: A")
        print(f"    A 在一对一中击败 B 和 C")
    else:
        print(f"  {Color.RED}✗{Color.END} Condorcet 获胜者错误")
        return False

    print(f"\n{Color.CYAN}测试 4: Condorcet 悖论{Color.END}")

    # Condorcet 悖论：循环偏好，无 Condorcet 获胜者
    votes_paradox = [
        ['A', 'B', 'C'],  # A > B > C
        ['B', 'C', 'A'],  # B > C > A
        ['C', 'A', 'B']   # C > A > B
    ]

    condorcet_paradox = condorcet_winner(votes_paradox)

    if condorcet_paradox is None:
        print(f"  {Color.GREEN}✓{Color.END} 正确识别 Condorcet 悖论")
        print(f"    循环：A>B, B>C, C>A")
        print(f"    {Color.YELLOW}没有 Condorcet 获胜者！{Color.END}")
    else:
        print(f"  {Color.RED}✗{Color.END} 应该没有 Condorcet 获胜者")
        return False

    print(f"\n{Color.CYAN}测试 5: 策略投票示例{Color.END}")

    # 3个投票者，候选人 A, B, C
    # 投票者1真实偏好: A > B > C
    # 投票者2偏好: B > C > A
    # 投票者3偏好: C > B > A

    print(f"  {Color.YELLOW}场景：{Color.END}")
    print(f"    投票者1真实偏好: A > B > C")
    print(f"    投票者2偏好: B > C > A")
    print(f"    投票者3偏好: C > B > A")
    print(f"    ")
    print(f"    诚实投票（多数规则）：")
    print(f"      每人1票，可能三方平局或随机")
    print(f"    ")
    print(f"    投票者1的策略：")
    print(f"      如果把票投给B（谎报为 B > A > C）")
    print(f"      B 可能获胜，这对投票者1比 C 获胜更好")
    print(f"    ")
    print(f"    {Color.RED}这就是策略投票！{Color.END}")

    print(f"\n{Color.CYAN}测试 6: Gibbard-Satterthwaite 定理{Color.END}")

    print(f"  {Color.YELLOW}定理内容：{Color.END}")
    print(f"    假设：")
    print(f"    1. 至少3个候选人")
    print(f"    2. 投票规则不是独裁的")
    print(f"    3. 投票规则满足：任何候选人都可能获胜")
    print(f"    ")
    print(f"    结论：")
    print(f"    该投票规则可被策略操纵")
    print(f"    ")
    print(f"    {Color.RED}没有完美的投票规则！{Color.END}")

    print(f"\n{Color.CYAN}测试 7: 不同规则的比较{Color.END}")

    votes_compare = [
        ['A', 'C', 'B'],
        ['A', 'C', 'B'],
        ['B', 'A', 'C'],
        ['C', 'B', 'A'],
        ['C', 'B', 'A']
    ]

    print(f"  {Color.YELLOW}投票情况：{Color.END}")
    print(f"    2人: A > C > B")
    print(f"    1人: B > A > C")
    print(f"    2人: C > B > A")

    plur = plurality_voting(votes_compare)
    borda = borda_count(votes_compare)
    cond = condorcet_winner(votes_compare)

    print(f"    ")
    print(f"    多数规则: {plur} (A和C各2票首选)")
    print(f"    Borda计数: {borda}")
    print(f"    Condorcet: {cond}")
    print(f"    ")
    print(f"    {Color.YELLOW}不同规则可能产生不同结果！{Color.END}")

    print(f"\n{Color.YELLOW}💡 投票理论的启示：{Color.END}")
    print(f"{Color.YELLOW}   - 没有完美的投票规则（Arrow 不可能定理）{Color.END}")
    print(f"{Color.YELLOW}   - 所有规则都可能被操纵（Gibbard-Satterthwaite）{Color.END}")
    print(f"{Color.YELLOW}   - 不同规则适合不同场景{Color.END}")
    print(f"{Color.YELLOW}   - 应用：选举、决策系统、推荐算法{Color.END}")

    return True


if __name__ == '__main__':
    test()
