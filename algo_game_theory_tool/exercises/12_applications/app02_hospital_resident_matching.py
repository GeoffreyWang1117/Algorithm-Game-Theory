"""
练习 21: 医院-住院医匹配系统 (Hospital-Resident Matching / NRMP)

这是匹配理论最著名的实际应用！美国的住院医师匹配项目(NRMP)
每年为数万名医学毕业生和医院进行匹配。

背景：
- 1940年代之前：医院竞相"抢"医生，导致混乱
- 1952年：NRMP成立，使用集中匹配算法
- 1984年：Roth证明NRMP使用的是Gale-Shapley算法的变体
- 2012年：Roth因匹配市场设计获得诺贝尔经济学奖

问题特点：
1. 医院有多个职位（vs 1对1婚姻匹配）
2. 需要考虑couples（夫妻医生希望在同一城市）
3. 稳定性至关重要（避免私下交易）

任务：实现医院-住院医匹配系统，支持多对一匹配和情侣约束。
"""

from typing import List, Dict, Set, Tuple, Optional


class Resident:
    """住院医生"""

    def __init__(self, resident_id: str, preferences: List[str],
                 partner_id: Optional[str] = None):
        """
        初始化住院医生

        参数:
            resident_id: 医生ID
            preferences: 医院偏好列表（按优先级排序）
            partner_id: 配偶ID（如果是couple）
        """
        self.id = resident_id
        self.preferences = preferences
        self.partner_id = partner_id
        self.current_hospital = None


class Hospital:
    """医院"""

    def __init__(self, hospital_id: str, capacity: int, preferences: List[str]):
        """
        初始化医院

        参数:
            hospital_id: 医院ID
            capacity: 职位数量
            preferences: 对医生的偏好列表
        """
        self.id = hospital_id
        self.capacity = capacity
        self.preferences = preferences
        self.matched_residents = []  # 当前匹配的医生列表


class HospitalResidentMatching:
    """医院-住院医匹配系统"""

    def __init__(self, residents: List[Resident], hospitals: List[Hospital]):
        """
        初始化匹配系统

        参数:
            residents: 医生列表
            hospitals: 医院列表
        """
        # TODO: 初始化
        pass

    def run_resident_proposing_algorithm(self) -> Dict[str, str]:
        """
        运行医生提议算法（Gale-Shapley多对一版本）

        算法：
        1. 每个未匹配的医生向偏好列表中下一个医院提议
        2. 每个医院考虑所有提议（包括已匹配的医生）
        3. 医院接受最偏好的capacity个医生，拒绝其他
        4. 被拒绝的医生继续向下一个医院提议
        5. 重复直到无医生可提议

        返回:
            dict: {resident_id: hospital_id} 匹配结果
        """
        # TODO: 实现医生提议算法
        pass

    def run_hospital_proposing_algorithm(self) -> Dict[str, str]:
        """
        运行医院提议算法

        这个算法对医院最优，对医生最差（对偶）

        返回:
            dict: {resident_id: hospital_id} 匹配结果
        """
        # TODO: 实现医院提议算法（可选）
        pass

    def is_stable_matching(self, matching: Dict[str, str]) -> Tuple[bool, List]:
        """
        检查匹配是否稳定

        稳定性条件：不存在阻塞对(r, h)使得：
        1. r更偏好h而非当前匹配
        2. h更偏好r而非当前某个匹配的医生（或有空位）

        参数:
            matching: 匹配结果

        返回:
            tuple: (is_stable, blocking_pairs)
        """
        # TODO: 检查稳定性
        pass

    def handle_couples(self, couples: List[Tuple[str, str]]) -> Dict[str, str]:
        """
        处理couple约束（挑战性！）

        Couple约束：两个医生希望在同一地理区域工作

        注意：加入couple约束后，稳定匹配可能不存在！

        参数:
            couples: 情侣对列表 [(resident1_id, resident2_id), ...]

        返回:
            dict: 尽可能满足couple约束的匹配
        """
        # TODO: 处理couple约束（高级功能）
        # 这是一个NP-hard问题！
        pass

    def compute_welfare_metrics(self, matching: Dict[str, str]) -> Dict:
        """
        计算匹配的福利指标

        返回:
            dict: {
                'resident_avg_rank': 医生平均获得第几志愿,
                'hospital_avg_rank': 医院平均获得第几志愿,
                'unmatched_residents': 未匹配医生数,
                'unfilled_positions': 未填满职位数
            }
        """
        # TODO: 计算福利指标
        pass


# HINT: 多对一匹配是1对1匹配的推广
# HINT: 医院可以临时接受多个医生，然后保留最好的capacity个
# HINT: 算法保证稳定性和终止性
# HINT: Couple问题很难！可能需要启发式算法


def test():
    """测试函数"""
    from exercise_runner import Color

    print(f"{Color.CYAN}测试 1: 创建匹配系统{Color.END}")

    # 创建医生
    residents = [
        Resident('R1', ['H1', 'H2', 'H3']),
        Resident('R2', ['H2', 'H1', 'H3']),
        Resident('R3', ['H1', 'H3', 'H2']),
        Resident('R4', ['H3', 'H1', 'H2'])
    ]

    # 创建医院（每个医院2个职位）
    hospitals = [
        Hospital('H1', capacity=2, preferences=['R1', 'R3', 'R2', 'R4']),
        Hospital('H2', capacity=1, preferences=['R2', 'R1', 'R4', 'R3']),
        Hospital('H3', capacity=1, preferences=['R3', 'R4', 'R1', 'R2'])
    ]

    matching_system = HospitalResidentMatching(residents, hospitals)
    print(f"  {Color.GREEN}✓{Color.END} 创建了4个医生和3个医院")

    print(f"\n{Color.CYAN}测试 2: 运行匹配算法{Color.END}")

    matching = matching_system.run_resident_proposing_algorithm()

    if matching:
        print(f"  {Color.GREEN}✓{Color.END} 匹配完成:")
        for resident_id, hospital_id in sorted(matching.items()):
            print(f"    {resident_id} → {hospital_id}")
    else:
        print(f"  {Color.RED}✗{Color.END} 请完成匹配算法实现")
        return False

    print(f"\n{Color.CYAN}测试 3: 验证稳定性{Color.END}")

    is_stable, blocking_pairs = matching_system.is_stable_matching(matching)

    if is_stable:
        print(f"  {Color.GREEN}✓{Color.END} 匹配是稳定的（无阻塞对）")
    else:
        print(f"  {Color.RED}✗{Color.END} 匹配不稳定")
        print(f"    阻塞对: {blocking_pairs}")
        return False

    print(f"\n{Color.CYAN}测试 4: 福利指标{Color.END}")

    metrics = matching_system.compute_welfare_metrics(matching)

    if metrics:
        print(f"  {Color.GREEN}✓{Color.END} 福利指标:")
        print(f"    医生平均志愿: {metrics.get('resident_avg_rank', 'N/A'):.2f}")
        print(f"    医院平均志愿: {metrics.get('hospital_avg_rank', 'N/A'):.2f}")
        print(f"    未匹配医生: {metrics.get('unmatched_residents', 0)}")
        print(f"    未填满职位: {metrics.get('unfilled_positions', 0)}")

    print(f"\n{Color.CYAN}测试 5: NRMP实际应用{Color.END}")

    print(f"  {Color.YELLOW}美国住院医师匹配项目 (NRMP):{Color.END}")
    print(f"    - 成立时间: 1952年")
    print(f"    - 参与者: ~40,000医学生 + ~30,000职位/年")
    print(f"    - 成功率: ~95% 医学生获得匹配")
    print(f"    - 算法: Gale-Shapley (医生提议)")
    print(f"    ")
    print(f"    关键成功因素:")
    print(f"      1. 稳定性保证（避免私下交易）")
    print(f"      2. 策略简单（诚实偏好接近最优）")
    print(f"      3. 公平性（双方都满意）")
    print(f"      4. 可扩展性（处理数万参与者）")

    print(f"\n{Color.CYAN}测试 6: Couple问题{Color.END}")

    print(f"  {Color.YELLOW}Couple匹配的挑战:{Color.END}")
    print(f"    问题: 夫妻医生希望在同一城市工作")
    print(f"    ")
    print(f"    理论结果:")
    print(f"      - 稳定匹配可能不存在！")
    print(f"      - 即使存在，找到它是NP-hard")
    print(f"    ")
    print(f"    实践解决方案:")
    print(f"      - NRMP使用启发式算法")
    print(f"      - 大多数情况下能找到好的匹配")
    print(f"      - ~95%的couple获得满意结果")

    print(f"\n{Color.CYAN}测试 7: 其他应用{Color.END}")

    print(f"  {Color.YELLOW}匹配理论的其他应用:{Color.END}")
    print(f"    1. 学校选择 (School Choice)")
    print(f"       - 纽约市、波士顿公立学校")
    print(f"       - 50万+ 学生")
    print(f"    ")
    print(f"    2. 肾脏交换 (Kidney Exchange)")
    print(f"       - 配对肾脏捐赠者和接受者")
    print(f"       - 拯救生命")
    print(f"    ")
    print(f"    3. 大学录取 (College Admissions)")
    print(f"       - 日本、土耳其等国家")
    print(f"    ")
    print(f"    4. 实习匹配 (Internship Matching)")
    print(f"       - 经济学、计算机等领域")

    print(f"\n{Color.YELLOW}💡 NRMP的历史意义：{Color.END}")
    print(f"{Color.YELLOW}   - 解决了医疗行业的混乱局面{Color.END}")
    print(f"{Color.YELLOW}   - 算法博弈论应用于市场设计{Color.END}")
    print(f"{Color.YELLOW}   - Alvin Roth 2012年诺贝尔经济学奖{Color.END}")
    print(f"{Color.YELLOW}   - 启发了众多其他匹配市场设计{Color.END}")

    return True


if __name__ == '__main__':
    test()
