"""
Deferred Acceptance算法实现

Gale-Shapley经典算法 + Roth-Peranson扩展（couples）
"""

import numpy as np
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import deque
import yaml


@dataclass
class Resident:
    """住院医"""
    id: str
    preferences: List[str]  # 医院ID列表（按偏好排序）
    scores: Dict[str, float] = field(default_factory=dict)  # USMLE等分数

    def prefers(self, h1: str, h2: str) -> bool:
        """是否prefer h1 over h2"""
        try:
            idx1 = self.preferences.index(h1)
            idx2 = self.preferences.index(h2)
            return idx1 < idx2
        except ValueError:
            # 不在列表中视为不可接受
            return False

    def get_rank(self, hospital: str) -> int:
        """获取医院在偏好列表中的排名（1-indexed）"""
        try:
            return self.preferences.index(hospital) + 1
        except ValueError:
            return float('inf')


@dataclass
class Hospital:
    """医院/项目"""
    id: str
    capacity: int
    preferences: List[str]  # 住院医ID列表（按偏好排序）
    location: Tuple[float, float] = (0.0, 0.0)  # (lat, lon)

    def prefers(self, r1: str, r2: str) -> bool:
        """是否prefer r1 over r2"""
        try:
            idx1 = self.preferences.index(r1)
            idx2 = self.preferences.index(r2)
            return idx1 < idx2
        except ValueError:
            return False

    def get_rank(self, resident: str) -> int:
        """获取住院医在偏好列表中的排名"""
        try:
            return self.preferences.index(resident) + 1
        except ValueError:
            return float('inf')


@dataclass
class Couple:
    """夫妻对"""
    id: str
    resident1_id: str
    resident2_id: str
    joint_preferences: List[Tuple[str, str]]  # [(h1, h2), ...] 联合偏好

    def prefers(self, pair1: Tuple[str, str], pair2: Tuple[str, str]) -> bool:
        """是否prefer pair1 over pair2"""
        try:
            idx1 = self.joint_preferences.index(pair1)
            idx2 = self.joint_preferences.index(pair2)
            return idx1 < idx2
        except ValueError:
            return False


class DeferredAcceptanceAlgorithm:
    """Deferred Acceptance算法基类"""

    def __init__(self, residents: List[Resident], hospitals: List[Hospital]):
        self.residents = {r.id: r for r in residents}
        self.hospitals = {h.id: h for h in hospitals}

    def run(self) -> Dict[str, str]:
        """运行算法，返回匹配结果"""
        raise NotImplementedError


class ResidentProposingDA(DeferredAcceptanceAlgorithm):
    """
    住院医提议版本的Deferred Acceptance

    性质：
    - Resident-optimal: 住院医获得所有稳定匹配中最preferred的
    - Hospital-pessimal: 医院获得所有稳定匹配中最不preferred的
    - Strategy-proof for residents: 提交真实偏好是dominant strategy
    """

    def run(self) -> Dict:
        """
        运行Resident-Proposing DA算法

        返回:
            dict: {
                'resident_matching': {resident_id: hospital_id},
                'hospital_matching': {hospital_id: [resident_ids]},
                'unmatched_residents': [resident_ids],
                'unfilled_positions': {hospital_id: num_unfilled}
            }
        """
        # 初始化
        free_residents = deque(self.residents.keys())
        proposal_count = {r_id: 0 for r_id in self.residents}

        # 医院的临时匹配（列表）
        hospital_matches = {h_id: [] for h_id in self.hospitals}

        # 迭代
        iteration = 0
        max_iterations = 100000

        while free_residents and iteration < max_iterations:
            resident_id = free_residents.popleft()
            resident = self.residents[resident_id]

            # 检查是否还有可提议的医院
            if proposal_count[resident_id] >= len(resident.preferences):
                # 已遍历完所有偏好，保持未匹配
                continue

            # 提议给下一个preferred医院
            hospital_id = resident.preferences[proposal_count[resident_id]]
            proposal_count[resident_id] += 1

            hospital = self.hospitals[hospital_id]

            # 医院考虑这个提议
            hospital_matches[hospital_id].append(resident_id)

            # 按医院的偏好排序
            hospital_matches[hospital_id].sort(
                key=lambda r_id: hospital.preferences.index(r_id)
                if r_id in hospital.preferences else float('inf')
            )

            # 拒绝超出容量的住院医
            while len(hospital_matches[hospital_id]) > hospital.capacity:
                rejected_id = hospital_matches[hospital_id].pop()
                free_residents.append(rejected_id)

            iteration += 1

        # 构建最终匹配
        resident_matching = {}
        for h_id, r_ids in hospital_matches.items():
            for r_id in r_ids:
                resident_matching[r_id] = h_id

        # 找出未匹配的住院医
        unmatched_residents = [
            r_id for r_id in self.residents
            if r_id not in resident_matching
        ]

        # 计算未填满的职位
        unfilled_positions = {}
        for h_id, hospital in self.hospitals.items():
            filled = len(hospital_matches[h_id])
            if filled < hospital.capacity:
                unfilled_positions[h_id] = hospital.capacity - filled

        return {
            'resident_matching': resident_matching,
            'hospital_matching': hospital_matches,
            'unmatched_residents': unmatched_residents,
            'unfilled_positions': unfilled_positions,
            'iterations': iteration
        }


class HospitalProposingDA(DeferredAcceptanceAlgorithm):
    """
    医院提议版本的Deferred Acceptance

    性质：
    - Hospital-optimal: 医院获得所有稳定匹配中最preferred的
    - Resident-pessimal: 住院医获得所有稳定匹配中最不preferred的
    - NOT strategy-proof for residents: 住院医可能通过操纵获利
    """

    def run(self) -> Dict:
        """运行Hospital-Proposing DA算法"""
        # 初始化
        hospitals_with_openings = set(self.hospitals.keys())
        proposal_count = {h_id: 0 for h_id in self.hospitals}

        # 住院医的临时匹配（单个）
        resident_matches = {}

        iteration = 0
        max_iterations = 100000

        while hospitals_with_openings and iteration < max_iterations:
            hospital_id = hospitals_with_openings.pop()
            hospital = self.hospitals[hospital_id]

            # 当前匹配数
            current_matches = sum(
                1 for r_id, h_id in resident_matches.items()
                if h_id == hospital_id
            )

            # 如果还有空位
            if current_matches < hospital.capacity:
                # 检查是否还有可提议的住院医
                if proposal_count[hospital_id] >= len(hospital.preferences):
                    continue

                # 提议给下一个preferred住院医
                resident_id = hospital.preferences[proposal_count[hospital_id]]
                proposal_count[hospital_id] += 1

                resident = self.residents[resident_id]

                # 住院医考虑这个提议
                if resident_id not in resident_matches:
                    # 当前未匹配，接受
                    resident_matches[resident_id] = hospital_id
                    hospitals_with_openings.add(hospital_id)  # 可能还有空位

                else:
                    # 已有匹配，比较
                    current_hospital_id = resident_matches[resident_id]

                    if resident.prefers(hospital_id, current_hospital_id):
                        # prefer新提议，拒绝旧匹配
                        resident_matches[resident_id] = hospital_id

                        # 旧医院有空位了
                        hospitals_with_openings.add(current_hospital_id)
                        hospitals_with_openings.add(hospital_id)
                    else:
                        # prefer当前匹配，拒绝新提议
                        hospitals_with_openings.add(hospital_id)

            iteration += 1

        # 构建hospital_matching
        hospital_matches = {h_id: [] for h_id in self.hospitals}
        for r_id, h_id in resident_matches.items():
            hospital_matches[h_id].append(r_id)

        unmatched_residents = [
            r_id for r_id in self.residents
            if r_id not in resident_matches
        ]

        unfilled_positions = {}
        for h_id, hospital in self.hospitals.items():
            filled = len(hospital_matches[h_id])
            if filled < hospital.capacity:
                unfilled_positions[h_id] = hospital.capacity - filled

        return {
            'resident_matching': resident_matches,
            'hospital_matching': hospital_matches,
            'unmatched_residents': unmatched_residents,
            'unfilled_positions': unfilled_positions,
            'iterations': iteration
        }


class RothPeransonAlgorithm:
    """
    Roth-Peranson算法：处理couples的启发式算法

    NRMP实际使用的算法
    """

    def __init__(self, residents: List[Resident], hospitals: List[Hospital],
                 couples: List[Couple]):
        self.residents = {r.id: r for r in residents}
        self.hospitals = {h.id: h for h in hospitals}
        self.couples = {c.id: c for c in couples}

        # 分离single residents和couple residents
        couple_resident_ids = set()
        for couple in couples:
            couple_resident_ids.add(couple.resident1_id)
            couple_resident_ids.add(couple.resident2_id)

        self.single_residents = [
            r for r in residents if r.id not in couple_resident_ids
        ]
        self.couple_residents = [
            r for r in residents if r.id in couple_resident_ids
        ]

    def run(self, max_iterations: int = 1000) -> Dict:
        """
        运行Roth-Peranson算法

        策略:
        1. 初始化：单身住院医运行标准DA
        2. 迭代改进：调整couples匹配
        3. 收敛检查

        参数:
            max_iterations: 最大迭代次数

        返回:
            dict: 匹配结果
        """
        print(f"Running Roth-Peranson with {len(self.couples)} couples...")

        # 第一阶段：单身住院医的标准DA
        print("  Phase 1: Matching single residents...")

        single_da = ResidentProposingDA(self.single_residents, list(self.hospitals.values()))
        initial_matching = single_da.run()

        resident_matching = initial_matching['resident_matching'].copy()
        hospital_matching = {h: list(residents) for h, residents in
                            initial_matching['hospital_matching'].items()}

        # 第二阶段：处理couples
        print("  Phase 2: Accommodating couples...")

        for iteration in range(max_iterations):
            improved = False

            for couple in self.couples.values():
                r1_id = couple.resident1_id
                r2_id = couple.resident2_id

                # 当前匹配
                current_h1 = resident_matching.get(r1_id, None)
                current_h2 = resident_matching.get(r2_id, None)
                current_pair = (current_h1, current_h2)

                # 尝试找到更preferred的联合匹配
                for preferred_pair in couple.joint_preferences:
                    h1, h2 = preferred_pair

                    # 如果比当前更好
                    if couple.prefers(preferred_pair, current_pair):
                        # 检查是否可行（医院有空位或愿意替换）
                        if self._can_accommodate_couple(
                            r1_id, r2_id, h1, h2,
                            resident_matching, hospital_matching
                        ):
                            # 执行移动
                            self._move_couple(
                                r1_id, r2_id, h1, h2,
                                resident_matching, hospital_matching
                            )

                            improved = True
                            break

            if not improved:
                print(f"  Converged after {iteration + 1} iterations")
                break

        # 计算未匹配和未填满
        unmatched_residents = [
            r_id for r_id in self.residents
            if r_id not in resident_matching
        ]

        unfilled_positions = {}
        for h_id, hospital in self.hospitals.items():
            filled = len(hospital_matching.get(h_id, []))
            if filled < hospital.capacity:
                unfilled_positions[h_id] = hospital.capacity - filled

        return {
            'resident_matching': resident_matching,
            'hospital_matching': hospital_matching,
            'unmatched_residents': unmatched_residents,
            'unfilled_positions': unfilled_positions,
            'couples_iterations': iteration + 1
        }

    def _can_accommodate_couple(self, r1_id, r2_id, h1, h2,
                                resident_matching, hospital_matching) -> bool:
        """检查医院是否能容纳这对couple"""
        if h1 is None or h2 is None:
            # 至少一方不匹配
            return False

        hospital1 = self.hospitals[h1]
        hospital2 = self.hospitals[h2]

        # 检查容量
        current_h1 = hospital_matching.get(h1, [])
        current_h2 = hospital_matching.get(h2, [])

        # 如果r1已在h1或h2有空位
        available_h1 = (r1_id in current_h1) or (len(current_h1) < hospital1.capacity)
        available_h2 = (r2_id in current_h2) or (len(current_h2) < hospital2.capacity)

        return available_h1 and available_h2

    def _move_couple(self, r1_id, r2_id, h1, h2,
                    resident_matching, hospital_matching):
        """移动couple到新的医院对"""
        # 移除旧匹配
        old_h1 = resident_matching.get(r1_id)
        old_h2 = resident_matching.get(r2_id)

        if old_h1 and old_h1 in hospital_matching:
            if r1_id in hospital_matching[old_h1]:
                hospital_matching[old_h1].remove(r1_id)

        if old_h2 and old_h2 in hospital_matching:
            if r2_id in hospital_matching[old_h2]:
                hospital_matching[old_h2].remove(r2_id)

        # 添加新匹配
        resident_matching[r1_id] = h1
        resident_matching[r2_id] = h2

        if h1 not in hospital_matching:
            hospital_matching[h1] = []
        hospital_matching[h1].append(r1_id)

        if h2 not in hospital_matching:
            hospital_matching[h2] = []
        hospital_matching[h2].append(r2_id)


def demo():
    """演示Deferred Acceptance算法"""
    print("=" * 70)
    print("Deferred Acceptance算法演示")
    print("=" * 70)

    # 创建简单场景
    residents = [
        Resident(id='R1', preferences=['H1', 'H2', 'H3']),
        Resident(id='R2', preferences=['H2', 'H1', 'H3']),
        Resident(id='R3', preferences=['H1', 'H3', 'H2']),
        Resident(id='R4', preferences=['H3', 'H2', 'H1']),
    ]

    hospitals = [
        Hospital(id='H1', capacity=2, preferences=['R1', 'R3', 'R2', 'R4']),
        Hospital(id='H2', capacity=1, preferences=['R2', 'R1', 'R4', 'R3']),
        Hospital(id='H3', capacity=1, preferences=['R4', 'R3', 'R1', 'R2']),
    ]

    print("\n场景设置:")
    print("  住院医: 4人")
    print("  医院: 3个")
    print("  总职位: 4个")

    # Resident-Proposing
    print("\n" + "=" * 70)
    print("1. Resident-Proposing DA")
    print("=" * 70)

    rp_da = ResidentProposingDA(residents, hospitals)
    rp_result = rp_da.run()

    print("\n匹配结果:")
    for r_id, h_id in sorted(rp_result['resident_matching'].items()):
        resident = next(r for r in residents if r.id == r_id)
        rank = resident.get_rank(h_id)
        print(f"  {r_id} → {h_id} (Rank {rank})")

    print(f"\n未匹配: {rp_result['unmatched_residents']}")
    print(f"迭代次数: {rp_result['iterations']}")

    # Hospital-Proposing
    print("\n" + "=" * 70)
    print("2. Hospital-Proposing DA")
    print("=" * 70)

    hp_da = HospitalProposingDA(residents, hospitals)
    hp_result = hp_da.run()

    print("\n匹配结果:")
    for r_id, h_id in sorted(hp_result['resident_matching'].items()):
        resident = next(r for r in residents if r.id == r_id)
        rank = resident.get_rank(h_id)
        print(f"  {r_id} → {h_id} (Rank {rank})")

    print(f"\n未匹配: {hp_result['unmatched_residents']}")
    print(f"迭代次数: {hp_result['iterations']}")

    # 对比
    print("\n" + "=" * 70)
    print("Resident-Proposing vs Hospital-Proposing")
    print("=" * 70)

    rp_avg_rank = np.mean([
        residents[[r.id for r in residents].index(r_id)].get_rank(h_id)
        for r_id, h_id in rp_result['resident_matching'].items()
    ])

    hp_avg_rank = np.mean([
        residents[[r.id for r in residents].index(r_id)].get_rank(h_id)
        for r_id, h_id in hp_result['resident_matching'].items()
    ])

    print(f"\n住院医平均排名:")
    print(f"  Resident-Proposing: {rp_avg_rank:.2f}")
    print(f"  Hospital-Proposing: {hp_avg_rank:.2f}")
    print(f"\n  Resident-Proposing对住院医更有利！")


if __name__ == '__main__':
    demo()
