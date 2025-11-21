"""
稳定性检查器

验证匹配是否稳定（无blocking pairs）
"""

from typing import Dict, List, Tuple
from deferred_acceptance import Resident, Hospital


class StabilityChecker:
    """稳定性检查器"""

    def __init__(self, residents: List[Resident], hospitals: List[Hospital]):
        self.residents = {r.id: r for r in residents}
        self.hospitals = {h.id: h for h in hospitals}

    def verify_stability(self, matching: Dict) -> Dict:
        """
        验证匹配的稳定性

        稳定匹配的定义：
        不存在blocking pair (r, h)，使得:
        1. r没有匹配到h
        2. r prefer h over其当前匹配
        3. h prefer r over某个当前匹配的住院医（或有空位）

        参数:
            matching: {'resident_matching': {...}, 'hospital_matching': {...}}

        返回:
            dict: {
                'is_stable': bool,
                'blocking_pairs': [(r_id, h_id), ...],
                'num_blocking_pairs': int
            }
        """
        resident_matching = matching['resident_matching']
        hospital_matching = matching['hospital_matching']

        blocking_pairs = []

        # 检查每个住院医和每个医院的组合
        for r_id, resident in self.residents.items():
            current_h_id = resident_matching.get(r_id, None)

            for h_id in resident.preferences:
                # 如果已经匹配到这个医院，跳过
                if h_id == current_h_id:
                    break  # 后面的医院都不如当前的

                hospital = self.hospitals[h_id]
                current_residents = hospital_matching.get(h_id, [])

                # 情况1：医院有空位
                if len(current_residents) < hospital.capacity:
                    # Blocking pair!
                    blocking_pairs.append((r_id, h_id))
                    continue

                # 情况2：医院已满，但prefer这个住院医over某个当前的
                # 找到医院最不喜欢的当前住院医
                worst_current = None
                worst_rank = -1

                for curr_r_id in current_residents:
                    rank = hospital.get_rank(curr_r_id)
                    if rank > worst_rank:
                        worst_rank = rank
                        worst_current = curr_r_id

                # 检查是否prefer新住院医
                new_rank = hospital.get_rank(r_id)

                if new_rank < worst_rank:
                    # 医院prefer r_id over worst_current
                    blocking_pairs.append((r_id, h_id))

        is_stable = len(blocking_pairs) == 0

        return {
            'is_stable': is_stable,
            'blocking_pairs': blocking_pairs,
            'num_blocking_pairs': len(blocking_pairs)
        }

    def compute_satisfaction(self, matching: Dict) -> Dict:
        """
        计算匹配满意度

        参数:
            matching: 匹配结果

        返回:
            dict: 各种满意度指标
        """
        resident_matching = matching['resident_matching']

        # 住院医满意度（平均排名）
        resident_ranks = []
        for r_id, h_id in resident_matching.items():
            resident = self.residents[r_id]
            rank = resident.get_rank(h_id)
            resident_ranks.append(rank)

        avg_resident_rank = (sum(resident_ranks) / len(resident_ranks)
                            if resident_ranks else 0)

        # 医院满意度
        hospital_matching = matching['hospital_matching']
        hospital_ranks = []

        for h_id, r_ids in hospital_matching.items():
            hospital = self.hospitals[h_id]
            for r_id in r_ids:
                rank = hospital.get_rank(r_id)
                hospital_ranks.append(rank)

        avg_hospital_rank = (sum(hospital_ranks) / len(hospital_ranks)
                            if hospital_ranks else 0)

        # 匹配率
        match_rate = len(resident_matching) / len(self.residents)

        # 填充率
        total_capacity = sum(h.capacity for h in self.hospitals.values())
        total_matched = sum(len(r_ids) for r_ids in hospital_matching.values())
        fill_rate = total_matched / total_capacity

        return {
            'avg_resident_rank': avg_resident_rank,
            'avg_hospital_rank': avg_hospital_rank,
            'match_rate': match_rate,
            'fill_rate': fill_rate,
            'total_matched': total_matched,
            'total_capacity': total_capacity
        }

    def check_pareto_efficiency(self, matching: Dict) -> Dict:
        """
        检查帕累托效率

        如果不存在另一个稳定匹配使得:
        - 至少一个参与者更好
        - 没有人更差

        简化检查：是否存在Pareto改进
        """
        # 这需要枚举所有稳定匹配，计算复杂
        # 简化：检查是否有明显的改进机会

        resident_matching = matching['resident_matching']

        # 寻找可以互换的pair
        for r1_id, h1_id in resident_matching.items():
            for r2_id, h2_id in resident_matching.items():
                if r1_id == r2_id:
                    continue

                r1 = self.residents[r1_id]
                r2 = self.residents[r2_id]

                # 如果r1 prefer h2 over h1 AND r2 prefer h1 over h2
                if r1.prefers(h2_id, h1_id) and r2.prefers(h1_id, h2_id):
                    # 潜在的Pareto改进（但需要检查医院）
                    h1 = self.hospitals[h1_id]
                    h2 = self.hospitals[h2_id]

                    if h1.prefers(r2_id, r1_id) and h2.prefers(r1_id, r2_id):
                        # 找到Pareto改进！
                        return {
                            'is_pareto_efficient': False,
                            'improvement': f"{r1_id}↔{r2_id} between {h1_id}↔{h2_id}"
                        }

        return {
            'is_pareto_efficient': True
        }


def demo():
    """演示稳定性检查"""
    from deferred_acceptance import Resident, Hospital, ResidentProposingDA

    print("=" * 70)
    print("稳定性检查演示")
    print("=" * 70)

    # 创建场景
    residents = [
        Resident(id='R1', preferences=['H1', 'H2']),
        Resident(id='R2', preferences=['H2', 'H1']),
        Resident(id='R3', preferences=['H1', 'H2']),
    ]

    hospitals = [
        Hospital(id='H1', capacity=2, preferences=['R1', 'R2', 'R3']),
        Hospital(id='H2', capacity=1, preferences=['R3', 'R2', 'R1']),
    ]

    print("\n运行Resident-Proposing DA...")
    da = ResidentProposingDA(residents, hospitals)
    matching = da.run()

    print("\n匹配结果:")
    for r_id, h_id in sorted(matching['resident_matching'].items()):
        print(f"  {r_id} → {h_id}")

    # 检查稳定性
    print("\n" + "=" * 70)
    print("稳定性检查")
    print("=" * 70)

    checker = StabilityChecker(residents, hospitals)
    stability_result = checker.verify_stability(matching)

    print(f"\n稳定性: {stability_result['is_stable']}")
    print(f"Blocking pairs数量: {stability_result['num_blocking_pairs']}")

    if not stability_result['is_stable']:
        print("\nBlocking pairs:")
        for r_id, h_id in stability_result['blocking_pairs']:
            print(f"  ({r_id}, {h_id})")

    # 计算满意度
    print("\n" + "=" * 70)
    print("满意度分析")
    print("=" * 70)

    satisfaction = checker.compute_satisfaction(matching)

    print(f"\n住院医平均排名: {satisfaction['avg_resident_rank']:.2f}")
    print(f"医院平均排名: {satisfaction['avg_hospital_rank']:.2f}")
    print(f"匹配率: {satisfaction['match_rate']*100:.1f}%")
    print(f"填充率: {satisfaction['fill_rate']*100:.1f}%")

    # Pareto效率
    print("\n" + "=" * 70)
    print("Pareto效率检查")
    print("=" * 70)

    pareto = checker.check_pareto_efficiency(matching)
    print(f"\nPareto效率: {pareto['is_pareto_efficient']}")


if __name__ == '__main__':
    demo()
