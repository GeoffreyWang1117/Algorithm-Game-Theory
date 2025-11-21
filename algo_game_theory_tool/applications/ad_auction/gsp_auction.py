"""
GSP (Generalized Second Price) 拍卖实现

Google AdWords、Facebook Ads等平台使用的核心拍卖机制
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import yaml
from pathlib import Path


@dataclass
class Advertiser:
    """广告主"""
    id: str
    bid: float  # 出价（$/点击）
    quality_score: float  # 质量分 [0, 1]
    budget: float = float('inf')  # 预算
    daily_spend: float = 0.0  # 当日消耗

    @property
    def rank_score(self) -> float:
        """Rank Score = bid × quality_score"""
        return self.bid * self.quality_score

    @property
    def budget_remaining(self) -> float:
        """剩余预算"""
        return self.budget - self.daily_spend

    def can_afford(self, cost: float) -> bool:
        """是否有足够预算"""
        return self.budget_remaining >= cost


@dataclass
class AdSlot:
    """广告位"""
    position: int  # 位置（1=最好）
    ctr_multiplier: float  # CTR乘数
    base_ctr: float = 0.01  # 基础CTR

    @property
    def effective_ctr(self) -> float:
        """有效CTR"""
        return self.base_ctr * self.ctr_multiplier


@dataclass
class AuctionResult:
    """拍卖结果"""
    advertiser_id: str
    position: int
    price_per_click: float
    expected_clicks: float
    total_payment: float
    quality_score: float
    rank_score: float


class GSPAuction:
    """GSP拍卖机制"""

    def __init__(self, config_path: str = 'configs/auction_config.yaml'):
        """
        初始化GSP拍卖

        参数:
            config_path: 配置文件路径
        """
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.num_slots = self.config['ad_slots']['num_slots']
        self.reserve_price = self.config['ad_slots']['reserve_price']

        # 创建广告位
        self.slots = self._create_slots()

    def _create_slots(self) -> List[AdSlot]:
        """创建广告位列表"""
        slots = []
        position_ctr_decay = self.config['ad_slots']['position_ctr_decay']

        for position in range(1, self.num_slots + 1):
            ctr_mult = position_ctr_decay.get(position, 0.1)
            slots.append(AdSlot(position=position, ctr_multiplier=ctr_mult))

        return slots

    def run(self, advertisers: List[Advertiser],
            impressions: int = 1) -> List[AuctionResult]:
        """
        运行GSP拍卖

        步骤：
        1. 计算每个广告主的Rank Score
        2. 按Rank Score降序排序
        3. 分配广告位（top K）
        4. 计算支付（GSP规则）

        参数:
            advertisers: 广告主列表
            impressions: 展示次数

        返回:
            List[AuctionResult]: 拍卖结果列表
        """
        # 1. 过滤：移除出价低于底价的广告主
        valid_advertisers = [
            adv for adv in advertisers
            if adv.bid >= self.reserve_price
        ]

        if not valid_advertisers:
            return []

        # 2. 按Rank Score排序
        sorted_advertisers = sorted(
            valid_advertisers,
            key=lambda x: x.rank_score,
            reverse=True
        )

        # 3. 分配广告位并计算支付
        results = []

        for i, advertiser in enumerate(sorted_advertisers[:self.num_slots]):
            position = i + 1
            slot = self.slots[i]

            # GSP支付规则：next_rank_score / own_quality_score
            if i < len(sorted_advertisers) - 1:
                next_advertiser = sorted_advertisers[i + 1]
                price_per_click = next_advertiser.rank_score / advertiser.quality_score
            else:
                # 最后一位：支付底价
                price_per_click = self.reserve_price

            # 确保不低于底价
            price_per_click = max(price_per_click, self.reserve_price)

            # 计算预期点击数
            expected_clicks = slot.effective_ctr * impressions

            # 总支付
            total_payment = price_per_click * expected_clicks

            # 检查预算
            if not advertiser.can_afford(total_payment):
                # 预算不足，调整点击数
                affordable_clicks = advertiser.budget_remaining / price_per_click
                expected_clicks = min(expected_clicks, affordable_clicks)
                total_payment = price_per_click * expected_clicks

            result = AuctionResult(
                advertiser_id=advertiser.id,
                position=position,
                price_per_click=price_per_click,
                expected_clicks=expected_clicks,
                total_payment=total_payment,
                quality_score=advertiser.quality_score,
                rank_score=advertiser.rank_score
            )

            results.append(result)

            # 更新广告主消耗
            advertiser.daily_spend += total_payment

        return results

    def calculate_revenue(self, results: List[AuctionResult]) -> float:
        """计算平台总收入"""
        return sum(r.total_payment for r in results)

    def calculate_advertiser_utility(self, advertiser: Advertiser,
                                    result: AuctionResult,
                                    true_value_per_click: float) -> float:
        """
        计算广告主效用

        效用 = 价值 - 支付
             = (真实估值 × 点击数) - 总支付

        参数:
            advertiser: 广告主
            result: 拍卖结果
            true_value_per_click: 广告主的真实估值/点击

        返回:
            float: 效用
        """
        value = true_value_per_click * result.expected_clicks
        utility = value - result.total_payment
        return utility

    def is_truthful(self, advertisers: List[Advertiser],
                   true_values: Dict[str, float]) -> Dict:
        """
        检查真实性（Truthfulness）

        在GSP中，真实出价不一定是最优策略

        参数:
            advertisers: 广告主列表
            true_values: {advertiser_id: true_value_per_click}

        返回:
            dict: 真实性分析结果
        """
        truthful_results = self.run(advertisers)

        # 测试：如果某个广告主降低出价，效用是否会更高？
        manipulation_found = False

        for i, adv in enumerate(advertisers):
            original_bid = adv.bid
            true_value = true_values[adv.id]

            # 找到该广告主在真实出价下的结果
            original_result = next(
                (r for r in truthful_results if r.advertiser_id == adv.id),
                None
            )

            if not original_result:
                continue

            original_utility = self.calculate_advertiser_utility(
                adv, original_result, true_value
            )

            # 测试不同的出价（bid shading）
            for shading in [0.9, 0.8, 0.7, 0.6]:
                adv.bid = original_bid * shading

                manipulated_results = self.run(advertisers)
                manipulated_result = next(
                    (r for r in manipulated_results if r.advertiser_id == adv.id),
                    None
                )

                if manipulated_result:
                    manipulated_utility = self.calculate_advertiser_utility(
                        adv, manipulated_result, true_value
                    )

                    if manipulated_utility > original_utility:
                        manipulation_found = True
                        print(f"⚠ {adv.id} 可以通过降低出价提高效用:")
                        print(f"  原始出价: ${original_bid:.2f}, 效用: ${original_utility:.2f}")
                        print(f"  降低出价: ${adv.bid:.2f}, 效用: ${manipulated_utility:.2f}")
                        break

            # 恢复原始出价
            adv.bid = original_bid

        return {
            'is_truthful': not manipulation_found,
            'manipulable': manipulation_found
        }


class VCGAuction:
    """VCG拍卖（对比基准）"""

    def __init__(self, slots: List[AdSlot], reserve_price: float = 0.0):
        self.slots = slots
        self.reserve_price = reserve_price

    def run(self, advertisers: List[Advertiser],
            true_values: Dict[str, float],
            impressions: int = 1) -> List[AuctionResult]:
        """
        运行VCG拍卖

        VCG是真实的（truthful），但收入可能低于GSP

        参数:
            advertisers: 广告主列表
            true_values: 真实估值
            impressions: 展示次数

        返回:
            List[AuctionResult]: 拍卖结果
        """
        # 按真实估值排序
        sorted_advertisers = sorted(
            advertisers,
            key=lambda x: true_values[x.id],
            reverse=True
        )

        results = []

        for i, advertiser in enumerate(sorted_advertisers[:len(self.slots)]):
            slot = self.slots[i]

            # VCG支付 = 该广告主的社会成本
            # = 没有他时的社会福利 - 有他时其他人的社会福利

            # 简化计算：支付下一位的估值（类似第二价格）
            if i < len(sorted_advertisers) - 1:
                next_advertiser = sorted_advertisers[i + 1]
                price_per_click = true_values[next_advertiser.id]
            else:
                price_per_click = self.reserve_price

            expected_clicks = slot.effective_ctr * impressions
            total_payment = price_per_click * expected_clicks

            result = AuctionResult(
                advertiser_id=advertiser.id,
                position=i + 1,
                price_per_click=price_per_click,
                expected_clicks=expected_clicks,
                total_payment=total_payment,
                quality_score=advertiser.quality_score,
                rank_score=true_values[advertiser.id]
            )

            results.append(result)

        return results


def compare_mechanisms():
    """对比GSP和VCG"""
    print("=" * 70)
    print("GSP vs VCG 拍卖对比")
    print("=" * 70)

    # 创建广告主
    advertisers = [
        Advertiser(id='A', bid=3.0, quality_score=0.8, budget=1000),
        Advertiser(id='B', bid=2.5, quality_score=0.9, budget=1000),
        Advertiser(id='C', bid=2.0, quality_score=0.7, budget=1000),
        Advertiser(id='D', bid=1.5, quality_score=0.6, budget=1000),
    ]

    # 真实估值（通常高于出价）
    true_values = {
        'A': 3.5,
        'B': 3.0,
        'C': 2.5,
        'D': 2.0,
    }

    # 创建广告位
    slots = [
        AdSlot(position=1, ctr_multiplier=1.0, base_ctr=0.05),
        AdSlot(position=2, ctr_multiplier=0.6, base_ctr=0.05),
        AdSlot(position=3, ctr_multiplier=0.3, base_ctr=0.05),
    ]

    print("\n广告主信息:")
    print("-" * 70)
    for adv in advertisers:
        print(f"{adv.id}: 出价=${adv.bid:.2f}, 质量分={adv.quality_score:.2f}, "
              f"Rank Score={adv.rank_score:.2f}, 真实估值=${true_values[adv.id]:.2f}")

    # GSP拍卖
    print("\n" + "=" * 70)
    print("GSP拍卖结果")
    print("=" * 70)

    gsp = GSPAuction()
    gsp_results = gsp.run(advertisers, impressions=1000)

    print(f"\n{'广告主':<8} {'位置':<6} {'Rank':<8} {'支付/点击':<12} {'点击数':<8} {'总支付':<10}")
    print("-" * 70)

    gsp_revenue = 0
    for r in gsp_results:
        print(f"{r.advertiser_id:<8} {r.position:<6} {r.rank_score:<8.2f} "
              f"${r.price_per_click:<11.2f} {r.expected_clicks:<8.1f} ${r.total_payment:<9.2f}")
        gsp_revenue += r.total_payment

    print(f"\n平台总收入: ${gsp_revenue:.2f}")

    # 计算广告主效用
    print("\n广告主效用:")
    for r in gsp_results:
        adv = next(a for a in advertisers if a.id == r.advertiser_id)
        utility = gsp.calculate_advertiser_utility(adv, r, true_values[adv.id])
        print(f"  {r.advertiser_id}: ${utility:.2f}")

    # VCG拍卖
    print("\n" + "=" * 70)
    print("VCG拍卖结果")
    print("=" * 70)

    vcg = VCGAuction(slots=slots, reserve_price=0.5)
    vcg_results = vcg.run(advertisers, true_values, impressions=1000)

    print(f"\n{'广告主':<8} {'位置':<6} {'估值':<8} {'支付/点击':<12} {'点击数':<8} {'总支付':<10}")
    print("-" * 70)

    vcg_revenue = 0
    for r in vcg_results:
        print(f"{r.advertiser_id:<8} {r.position:<6} ${r.rank_score:<7.2f} "
              f"${r.price_per_click:<11.2f} {r.expected_clicks:<8.1f} ${r.total_payment:<9.2f}")
        vcg_revenue += r.total_payment

    print(f"\n平台总收入: ${vcg_revenue:.2f}")

    # 对比
    print("\n" + "=" * 70)
    print("机制对比")
    print("=" * 70)

    print(f"\nGSP收入: ${gsp_revenue:.2f}")
    print(f"VCG收入: ${vcg_revenue:.2f}")
    print(f"收入差异: ${gsp_revenue - vcg_revenue:.2f} ({(gsp_revenue/vcg_revenue - 1)*100:.1f}%)")

    # 真实性检查
    print("\n" + "=" * 70)
    print("真实性分析")
    print("=" * 70)

    truthfulness = gsp.is_truthful(advertisers, true_values)

    if truthfulness['is_truthful']:
        print("✓ GSP是真实的（在此配置下）")
    else:
        print("✗ GSP不是真实的（存在操纵空间）")

    print("\nVCG是理论上真实的（Truthful by design）")


if __name__ == '__main__':
    compare_mechanisms()
