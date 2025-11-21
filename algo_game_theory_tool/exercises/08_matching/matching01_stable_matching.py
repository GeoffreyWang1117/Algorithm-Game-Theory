"""
练习 13: 稳定匹配 (Stable Matching / Gale-Shapley Algorithm)

稳定匹配问题由 Gale 和 Shapley (1962) 提出，是匹配理论的基础。
Shapley 和 Roth 因匹配理论的贡献获得2012年诺贝尔经济学奖。

问题：给定 n 个男性和 n 个女性，每人对异性有偏好排序。
目标：找到一个稳定匹配，即不存在"阻塞对"。

阻塞对 (Blocking Pair)：
一对未匹配的男女 (m, w)，他们都更偏好对方而非当前伴侣。

Gale-Shapley 算法（求婚-拒绝算法）：
1. 每轮未匹配的男性向他最偏好的还未拒绝他的女性求婚
2. 每个女性选择她最偏好的求婚者（拒绝其他）
3. 重复直到所有人都匹配

性质：
- 总能找到稳定匹配
- 男性最优（每个男性获得他在所有稳定匹配中最好的伴侣）
- 女性最差（每个女性获得她在所有稳定匹配中最差的伴侣）

任务：实现 Gale-Shapley 算法并验证稳定性。
"""


def gale_shapley(men_preferences, women_preferences):
    """
    实现 Gale-Shapley 稳定匹配算法（男性求婚版本）

    参数:
        men_preferences: 男性偏好 {man: [women_in_preference_order]}
        women_preferences: 女性偏好 {woman: [men_in_preference_order]}

    返回:
        dict: 匹配结果 {man: woman}
    """
    # TODO: 实现 Gale-Shapley 算法
    # 1. 初始化：所有人未匹配
    # 2. 循环直到所有男性都匹配：
    #    - 每个未匹配男性向偏好列表中下一个女性求婚
    #    - 每个女性比较当前求婚者和现有伴侣，选择更偏好的
    # 3. 返回最终匹配
    pass


def is_stable_matching(matching, men_preferences, women_preferences):
    """
    检查匹配是否稳定（不存在阻塞对）

    参数:
        matching: 匹配结果 {man: woman}
        men_preferences: 男性偏好
        women_preferences: 女性偏好

    返回:
        tuple: (is_stable, blocking_pairs)
               is_stable: bool
               blocking_pairs: 阻塞对列表 [(man, woman), ...]
    """
    # TODO: 检查稳定性
    # 对每一对未匹配的 (m, w)：
    #   如果 m 更偏好 w 而非当前伴侣 AND w 更偏好 m 而非当前伴侣
    #   则 (m, w) 是阻塞对
    pass


def find_all_stable_matchings(men_preferences, women_preferences):
    """
    找出所有稳定匹配（挑战性练习！）

    提示：可以使用回溯搜索 + 稳定性检查
    对于小规模问题，枚举所有可能匹配并检查稳定性

    参数:
        men_preferences: 男性偏好
        women_preferences: 女性偏好

    返回:
        list: 所有稳定匹配的列表 [matching1, matching2, ...]
    """
    # TODO: 找出所有稳定匹配（可选）
    # 这是一个挑战性练习
    pass


def get_rank(person, preferences, partner):
    """
    获取 person 对 partner 的偏好排名（0是最喜欢）

    参数:
        person: 个体
        preferences: 偏好字典
        partner: 伴侣

    返回:
        int: 排名（0-indexed）
    """
    # TODO: 返回 partner 在 person 偏好列表中的位置
    pass


# HINT: Gale-Shapley 算法的关键：
#       - 男性从最喜欢的开始求婚
#       - 女性"暂时接受"更好的求婚者
#       - 算法保证终止且结果稳定
# HINT: 检查稳定性：遍历所有可能的 (m, w) 对，看是否形成阻塞


def test():
    """测试函数"""
    from exercise_runner import Color

    print(f"{Color.CYAN}测试 1: 简单的 2x2 稳定匹配{Color.END}")

    # 两个男性 M1, M2；两个女性 W1, W2
    men_pref = {
        'M1': ['W1', 'W2'],  # M1 更喜欢 W1
        'M2': ['W2', 'W1']   # M2 更喜欢 W2
    }

    women_pref = {
        'W1': ['M1', 'M2'],  # W1 更喜欢 M1
        'W2': ['M2', 'M1']   # W2 更喜欢 M2
    }

    matching = gale_shapley(men_pref, women_pref)

    # 期望匹配：(M1, W1), (M2, W2)
    if matching == {'M1': 'W1', 'M2': 'W2'}:
        print(f"  {Color.GREEN}✓{Color.END} 找到匹配: {matching}")
    else:
        print(f"  {Color.RED}✗{Color.END} 匹配错误")
        print(f"    期望: {{'M1': 'W1', 'M2': 'W2'}}")
        print(f"    实际: {matching}")
        return False

    print(f"\n{Color.CYAN}测试 2: 验证稳定性{Color.END}")

    is_stable, blocking = is_stable_matching(matching, men_pref, women_pref)

    if is_stable:
        print(f"  {Color.GREEN}✓{Color.END} 匹配是稳定的")
    else:
        print(f"  {Color.RED}✗{Color.END} 匹配不稳定")
        print(f"    阻塞对: {blocking}")
        return False

    print(f"\n{Color.CYAN}测试 3: 存在阻塞对的不稳定匹配{Color.END}")

    # 构造一个不稳定的匹配
    unstable_matching = {'M1': 'W2', 'M2': 'W1'}

    is_stable_2, blocking_2 = is_stable_matching(unstable_matching, men_pref, women_pref)

    if not is_stable_2 and len(blocking_2) > 0:
        print(f"  {Color.GREEN}✓{Color.END} 正确识别不稳定匹配")
        print(f"    阻塞对: {blocking_2}")
    else:
        print(f"  {Color.RED}✗{Color.END} 应该识别为不稳定")
        return False

    print(f"\n{Color.CYAN}测试 4: 经典例子（不同偏好）{Color.END}")

    # 经典的稳定匹配问题例子
    men_pref_2 = {
        'M1': ['W2', 'W1', 'W3'],
        'M2': ['W1', 'W2', 'W3'],
        'M3': ['W1', 'W2', 'W3']
    }

    women_pref_2 = {
        'W1': ['M2', 'M1', 'M3'],
        'W2': ['M1', 'M2', 'M3'],
        'W3': ['M1', 'M2', 'M3']
    }

    matching_2 = gale_shapley(men_pref_2, women_pref_2)
    is_stable_3, _ = is_stable_matching(matching_2, men_pref_2, women_pref_2)

    if is_stable_3:
        print(f"  {Color.GREEN}✓{Color.END} Gale-Shapley 产生稳定匹配")
        print(f"    匹配: {matching_2}")
    else:
        print(f"  {Color.RED}✗{Color.END} Gale-Shapley 应该总是产生稳定匹配")
        return False

    print(f"\n{Color.CYAN}测试 5: 偏好排名{Color.END}")

    rank = get_rank('M1', men_pref, 'W1')

    if rank == 0:  # W1 是 M1 的第一选择
        print(f"  {Color.GREEN}✓{Color.END} 偏好排名计算正确")
    else:
        print(f"  {Color.RED}✗{Color.END} 排名错误，W1 应该是 M1 的第一选择")
        return False

    print(f"\n{Color.YELLOW}💡 Gale-Shapley 算法的性质：{Color.END}")
    print(f"{Color.YELLOW}   - 总能找到稳定匹配（存在性）{Color.END}")
    print(f"{Color.YELLOW}   - O(n²) 时间复杂度{Color.END}")
    print(f"{Color.YELLOW}   - 男性最优：每个男性得到他在所有稳定匹配中最好的{Color.END}")
    print(f"{Color.YELLOW}   - 女性最差：每个女性得到她在所有稳定匹配中最差的{Color.END}")
    print(f"{Color.YELLOW}   - 应用：住院医生匹配、学校录取等{Color.END}")

    return True


if __name__ == '__main__':
    test()
