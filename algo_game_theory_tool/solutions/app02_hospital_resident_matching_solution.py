"""
练习 21 参考答案: 医院-住院医匹配系统

这是app02_hospital_resident_matching.py的完整参考实现。
"""

from typing import List, Dict, Set, Tuple, Optional
from collections import deque


class Resident:
    """住院医生"""

    def __init__(self, resident_id: str, preferences: List[str],
                 partner_id: Optional[str] = None):
        self.id = resident_id
        self.preferences = preferences
        self.partner_id = partner_id
        self.current_hospital = None
        self.proposal_index = 0  # 下一个要提议的医院索引


class Hospital:
    """医院"""

    def __init__(self, hospital_id: str, capacity: int, preferences: List[str]):
        self.id = hospital_id
        self.capacity = capacity
        self.preferences = preferences
        self.matched_residents = []


class HospitalResidentMatching:
    """医院-住院医匹配系统 - 完整实现"""

    def __init__(self, residents: List[Resident], hospitals: List[Hospital]):
        self.residents = {r.id: r for r in residents}
        self.hospitals = {h.id: h for h in hospitals}

    def run_resident_proposing_algorithm(self) -> Dict[str, str]:
        """
        运行医生提议算法 - 完整实现

        这是Gale-Shapley算法的多对一版本
        """
        # 重置状态
        for resident in self.residents.values():
            resident.current_hospital = None
            resident.proposal_index = 0

        for hospital in self.hospitals.values():
            hospital.matched_residents = []

        # 自由医生队列
        free_residents = deque(self.residents.values())

        while free_residents:
            resident = free_residents.popleft()

            # 如果医生已遍历完所有医院，保持未匹配状态
            if resident.proposal_index >= len(resident.preferences):
                continue

            # 向下一个医院提议
            hospital_id = resident.preferences[resident.proposal_index]
            resident.proposal_index += 1

            if hospital_id not in self.hospitals:
                # 无效医院，继续
                free_residents.append(resident)
                continue

            hospital = self.hospitals[hospital_id]

            # 医院考虑这个提议
            hospital.matched_residents.append(resident.id)

            # 医院根据偏好排序所有当前匹配的医生
            hospital.matched_residents.sort(
                key=lambda r_id: (
                    hospital.preferences.index(r_id)
                    if r_id in hospital.preferences
                    else len(hospital.preferences)
                )
            )

            # 如果超出容量，拒绝最不偏好的医生
            while len(hospital.matched_residents) > hospital.capacity:
                rejected_id = hospital.matched_residents.pop()
                rejected = self.residents[rejected_id]
                rejected.current_hospital = None
                free_residents.append(rejected)

            # 更新所有被接受医生的状态
            for r_id in hospital.matched_residents:
                self.residents[r_id].current_hospital = hospital_id

        # 构建最终匹配
        matching = {}
        for resident in self.residents.values():
            if resident.current_hospital:
                matching[resident.id] = resident.current_hospital

        return matching

    def run_hospital_proposing_algorithm(self) -> Dict[str, str]:
        """
        运行医院提议算法 - 完整实现

        这个算法对医院最优
        """
        # 重置状态
        for resident in self.residents.values():
            resident.current_hospital = None

        for hospital in self.hospitals.values():
            hospital.matched_residents = []

        # 每个医院维护提议索引
        hospital_proposal_index = {h_id: 0 for h_id in self.hospitals}

        # 未满的医院队列
        unfilled_hospitals = deque(self.hospitals.values())

        while unfilled_hospitals:
            hospital = unfilled_hospitals.popleft()

            # 如果医院已满或遍历完所有医生
            if (len(hospital.matched_residents) >= hospital.capacity or
                hospital_proposal_index[hospital.id] >= len(hospital.preferences)):
                continue

            # 向下一个医生提议
            resident_id = hospital.preferences[hospital_proposal_index[hospital.id]]
            hospital_proposal_index[hospital.id] += 1

            if resident_id not in self.residents:
                unfilled_hospitals.append(hospital)
                continue

            resident = self.residents[resident_id]

            # 医生比较当前提议和现有匹配
            if resident.current_hospital is None:
                # 未匹配，接受
                resident.current_hospital = hospital.id
                hospital.matched_residents.append(resident_id)
            else:
                # 已匹配，比较偏好
                current_hospital_id = resident.current_hospital
                current_rank = resident.preferences.index(current_hospital_id)
                new_rank = resident.preferences.index(hospital.id)

                if new_rank < current_rank:
                    # 更偏好新医院，拒绝旧医院
                    old_hospital = self.hospitals[current_hospital_id]
                    old_hospital.matched_residents.remove(resident_id)
                    unfilled_hospitals.append(old_hospital)

                    resident.current_hospital = hospital.id
                    hospital.matched_residents.append(resident_id)
                else:
                    # 拒绝新医院
                    unfilled_hospitals.append(hospital)

            # 如果医院未满，继续提议
            if len(hospital.matched_residents) < hospital.capacity:
                unfilled_hospitals.append(hospital)

        # 构建匹配
        matching = {}
        for resident in self.residents.values():
            if resident.current_hospital:
                matching[resident.id] = resident.current_hospital

        return matching

    def is_stable_matching(self, matching: Dict[str, str]) -> Tuple[bool, List]:
        """检查稳定性 - 完整实现"""
        blocking_pairs = []

        # 检查每个(医生, 医院)对
        for resident_id, resident in self.residents.items():
            current_hospital_id = matching.get(resident_id)

            for hospital_id in resident.preferences:
                # 医生是否更偏好这个医院
                if current_hospital_id is not None:
                    if hospital_id == current_hospital_id:
                        break  # 已经是当前医院，后面的都不偏好
                    current_rank = resident.preferences.index(current_hospital_id)
                    hospital_rank = resident.preferences.index(hospital_id)
                    if hospital_rank >= current_rank:
                        continue  # 不更偏好

                hospital = self.hospitals[hospital_id]

                # 医院是否愿意接受这个医生
                if len(hospital.matched_residents) < hospital.capacity:
                    # 有空位，形成阻塞对
                    blocking_pairs.append((resident_id, hospital_id))
                else:
                    # 检查是否比某个当前医生更偏好
                    resident_rank = (hospital.preferences.index(resident_id)
                                    if resident_id in hospital.preferences
                                    else len(hospital.preferences))

                    for matched_id in hospital.matched_residents:
                        matched_rank = (hospital.preferences.index(matched_id)
                                       if matched_id in hospital.preferences
                                       else len(hospital.preferences))

                        if resident_rank < matched_rank:
                            blocking_pairs.append((resident_id, hospital_id))
                            break

        return len(blocking_pairs) == 0, blocking_pairs

    def compute_welfare_metrics(self, matching: Dict[str, str]) -> Dict:
        """计算福利指标 - 完整实现"""
        metrics = {
            'resident_avg_rank': 0,
            'hospital_avg_rank': 0,
            'unmatched_residents': 0,
            'unfilled_positions': 0
        }

        # 医生平均志愿
        resident_ranks = []
        for resident_id, resident in self.residents.items():
            if resident_id in matching:
                hospital_id = matching[resident_id]
                rank = resident.preferences.index(hospital_id) + 1  # 1-indexed
                resident_ranks.append(rank)
            else:
                metrics['unmatched_residents'] += 1

        if resident_ranks:
            metrics['resident_avg_rank'] = sum(resident_ranks) / len(resident_ranks)

        # 医院平均志愿和未填满职位
        hospital_ranks = []
        for hospital_id, hospital in self.hospitals.items():
            matched_count = sum(1 for r_id, h_id in matching.items()
                              if h_id == hospital_id)

            if matched_count < hospital.capacity:
                metrics['unfilled_positions'] += hospital.capacity - matched_count

            # 计算医院获得的医生排名
            for resident_id in matching:
                if matching[resident_id] == hospital_id:
                    if resident_id in hospital.preferences:
                        rank = hospital.preferences.index(resident_id) + 1
                        hospital_ranks.append(rank)

        if hospital_ranks:
            metrics['hospital_avg_rank'] = sum(hospital_ranks) / len(hospital_ranks)

        return metrics

    def handle_couples(self, couples: List[Tuple[str, str]]) -> Dict[str, str]:
        """
        处理couple约束 - 简化启发式实现

        注意：这是一个NP-hard问题，这里提供一个简单的启发式
        """
        # 先运行标准算法
        matching = self.run_resident_proposing_algorithm()

        # 对每对couple，尝试改进
        for r1_id, r2_id in couples:
            h1_id = matching.get(r1_id)
            h2_id = matching.get(r2_id)

            if h1_id and h2_id:
                # 检查是否在同一地区（简化：检查医院ID前缀）
                # 实际应用中会有地理位置数据
                if self._same_region(h1_id, h2_id):
                    continue  # 已经满足

            # 尝试找到同一地区的匹配（启发式）
            # 这里省略复杂的重新匹配逻辑
            # 实际NRMP使用更复杂的算法

        return matching

    def _same_region(self, h1_id: str, h2_id: str) -> bool:
        """检查两个医院是否在同一地区（简化版）"""
        # 简化实现：假设医院ID首字母相同表示同一地区
        return h1_id[0] == h2_id[0] if h1_id and h2_id else False


def demonstrate_matching():
    """演示匹配算法"""
    print("=" * 70)
    print("医院-住院医匹配系统演示")
    print("=" * 70)

    # 创建示例
    residents = [
        Resident('Alice', ['MGH', 'BWH', 'UCSF']),
        Resident('Bob', ['BWH', 'MGH', 'UCSF']),
        Resident('Carol', ['UCSF', 'MGH', 'BWH']),
        Resident('Dave', ['MGH', 'UCSF', 'BWH']),
    ]

    hospitals = [
        Hospital('MGH', capacity=2, preferences=['Alice', 'Dave', 'Bob', 'Carol']),
        Hospital('BWH', capacity=1, preferences=['Bob', 'Alice', 'Carol', 'Dave']),
        Hospital('UCSF', capacity=1, preferences=['Carol', 'Dave', 'Alice', 'Bob'])
    ]

    system = HospitalResidentMatching(residents, hospitals)

    # 运行医生提议算法
    print("\n医生提议算法（对医生最优）：")
    print("-" * 70)
    matching_r = system.run_resident_proposing_algorithm()

    for r_id, h_id in sorted(matching_r.items()):
        r = system.residents[r_id]
        rank = r.preferences.index(h_id) + 1
        print(f"  {r_id} → {h_id} (第{rank}志愿)")

    metrics_r = system.compute_welfare_metrics(matching_r)
    print(f"\n  医生平均志愿: {metrics_r['resident_avg_rank']:.2f}")

    # 运行医院提议算法
    print("\n医院提议算法（对医院最优）：")
    print("-" * 70)
    matching_h = system.run_hospital_proposing_algorithm()

    for r_id, h_id in sorted(matching_h.items()):
        h = system.hospitals[h_id]
        rank = h.preferences.index(r_id) + 1
        print(f"  {r_id} → {h_id} (医院第{rank}偏好)")

    metrics_h = system.compute_welfare_metrics(matching_h)
    print(f"\n  医院平均偏好排名: {metrics_h['hospital_avg_rank']:.2f}")

    # 验证稳定性
    print("\n稳定性检查：")
    print("-" * 70)
    is_stable_r, _ = system.is_stable_matching(matching_r)
    is_stable_h, _ = system.is_stable_matching(matching_h)

    print(f"  医生提议匹配稳定: {is_stable_r}")
    print(f"  医院提议匹配稳定: {is_stable_h}")


if __name__ == '__main__':
    demonstrate_matching()

    print("\n" + "=" * 70)
    print("运行单元测试")
    print("=" * 70)

    from app02_hospital_resident_matching import test
    test()
