"""
练习 20 参考答案: 广告拍卖系统

这是app01_ad_auction.py的完整参考实现。
"""

from typing import List, Dict, Tuple


class Advertiser:
    """广告主"""

    def __init__(self, advertiser_id: str, bid: float, quality_score: float):
        self.id = advertiser_id
        self.bid = bid
        self.quality_score = quality_score
        self.rank_score = bid * quality_score


class AdSlot:
    """广告位"""

    def __init__(self, position: int, ctr: float):
        self.position = position
        self.ctr = ctr


class SponsoredSearchAuction:
    """广告搜索拍卖系统 - 完整实现"""

    def __init__(self, slots: List[AdSlot]):
        self.slots = sorted(slots, key=lambda x: x.position)  # 按位置排序

    def run_gsp_auction(self, advertisers: List[Advertiser]) -> Dict:
        """
        运行GSP拍卖 - 完整实现

        实现思路：
        1. 按rank_score降序排序广告主
        2. 前N个广告主获得广告位（N=广告位数量）
        3. 计算支付：使用GSP规则
        """
        # 1. 按rank_score排序（降序）
        sorted_advertisers = sorted(advertisers,
                                   key=lambda x: x.rank_score,
                                   reverse=True)

        # 2. 分配广告位
        allocation = {}  # advertiser_id -> slot_position
        payments = {}    # advertiser_id -> payment
        clicks = {}      # advertiser_id -> expected_clicks

        # 只有前len(slots)个广告主能获得广告位
        n_slots = len(self.slots)

        for i in range(min(n_slots, len(sorted_advertisers))):
            advertiser = sorted_advertisers[i]
            slot = self.slots[i]

            # 分配广告位
            allocation[advertiser.id] = slot.position

            # 计算期望点击数
            # 实际CTR = 基础CTR × (advertiser的quality相关因子)
            # 简化模型：直接使用slot的CTR
            expected_clicks = slot.ctr * 100  # 假设100次展示
            clicks[advertiser.id] = expected_clicks

            # 计算支付（GSP规则）
            if i < len(sorted_advertisers) - 1 and i < n_slots - 1:
                # 有下一位竞争者
                next_advertiser = sorted_advertisers[i + 1]
                # 支付 = (下一位的rank_score / 自己的quality_score) × 点击数
                price_per_click = next_advertiser.rank_score / advertiser.quality_score
                total_payment = price_per_click * expected_clicks
            else:
                # 最后一位或没有竞争者，支付保留价（通常为0或最小值）
                total_payment = 0.01 * expected_clicks  # 最小价格

            payments[advertiser.id] = total_payment

        return {
            'allocation': allocation,
            'payments': payments,
            'clicks': clicks
        }

    def calculate_revenue(self, allocation: Dict, payments: Dict) -> float:
        """计算拍卖总收入 - 完整实现"""
        return sum(payments.values())

    def is_truthful_bidding_optimal(self, advertiser: Advertiser,
                                    other_advertisers: List[Advertiser],
                                    true_value_per_click: float) -> bool:
        """
        检查真实出价是否最优

        GSP不是激励相容的！这个函数演示为什么。
        """
        # 计算真实出价的效用
        all_advertisers_truthful = other_advertisers + [advertiser]
        result_truthful = self.run_gsp_auction(all_advertisers_truthful)

        if advertiser.id in result_truthful['allocation']:
            clicks_truthful = result_truthful['clicks'][advertiser.id]
            payment_truthful = result_truthful['payments'][advertiser.id]
            utility_truthful = clicks_truthful * true_value_per_click - payment_truthful
        else:
            utility_truthful = 0

        # 尝试一些策略性出价
        test_bids = [advertiser.bid * 0.8, advertiser.bid * 1.2,
                    advertiser.bid * 0.5, advertiser.bid * 1.5]

        for test_bid in test_bids:
            strategic_advertiser = Advertiser(advertiser.id, test_bid,
                                             advertiser.quality_score)
            all_advertisers_strategic = other_advertisers + [strategic_advertiser]
            result_strategic = self.run_gsp_auction(all_advertisers_strategic)

            if strategic_advertiser.id in result_strategic['allocation']:
                clicks_strategic = result_strategic['clicks'][strategic_advertiser.id]
                payment_strategic = result_strategic['payments'][strategic_advertiser.id]
                utility_strategic = clicks_strategic * true_value_per_click - payment_strategic

                # 如果策略性出价更好，则真实出价不是最优
                if utility_strategic > utility_truthful + 0.01:  # 容差
                    return False

        return True


def demonstrate_gsp_mechanism():
    """演示GSP机制"""
    print("=" * 60)
    print("GSP广告拍卖机制演示")
    print("=" * 60)

    # 创建广告位
    slots = [
        AdSlot(position=1, ctr=0.10),
        AdSlot(position=2, ctr=0.06),
        AdSlot(position=3, ctr=0.03)
    ]

    # 创建广告主
    advertisers = [
        Advertiser('Nike', bid=5.0, quality_score=9),
        Advertiser('Adidas', bid=4.5, quality_score=10),
        Advertiser('Puma', bid=6.0, quality_score=7),
        Advertiser('Reebok', bid=3.0, quality_score=8)
    ]

    # 运行拍卖
    auction = SponsoredSearchAuction(slots)
    result = auction.run_gsp_auction(advertisers)

    # 显示结果
    print("\n排名和分配：")
    print("-" * 60)
    sorted_alloc = sorted(result['allocation'].items(), key=lambda x: x[1])

    for adv_id, position in sorted_alloc:
        # 找到对应的广告主
        adv = next(a for a in advertisers if a.id == adv_id)
        clicks = result['clicks'][adv_id]
        payment = result['payments'][adv_id]
        cpc = payment / clicks if clicks > 0 else 0

        print(f"\n位置 {position}: {adv_id}")
        print(f"  出价: ${adv.bid:.2f}")
        print(f"  质量得分: {adv.quality_score}")
        print(f"  排名得分: {adv.rank_score:.2f}")
        print(f"  期望点击: {clicks:.2f}")
        print(f"  总支付: ${payment:.2f}")
        print(f"  实际CPC: ${cpc:.2f}")

    revenue = auction.calculate_revenue(result['allocation'], result['payments'])
    print(f"\n总收入: ${revenue:.2f}")

    # 分析激励相容性
    print("\n" + "=" * 60)
    print("激励相容性分析")
    print("=" * 60)

    nike = next(a for a in advertisers if a.id == 'Nike')
    others = [a for a in advertisers if a.id != 'Nike']

    # 假设Nike的真实价值是每次点击$6
    is_truthful = auction.is_truthful_bidding_optimal(nike, others, 6.0)

    print(f"\nNike真实价值: $6.00/点击")
    print(f"Nike当前出价: ${nike.bid:.2f}")
    print(f"真实出价是否最优: {is_truthful}")

    if not is_truthful:
        print("\n⚠️  GSP不是激励相容的！")
        print("   存在更好的策略性出价")
    else:
        print("\n在这个例子中，真实出价恰好是最优的")


def compare_gsp_vcg():
    """比较GSP和VCG"""
    print("\n" + "=" * 60)
    print("GSP vs VCG 比较")
    print("=" * 60)

    comparison = """
    | 特性              | VCG                    | GSP                    |
    |-------------------|------------------------|------------------------|
    | 激励相容          | ✓ 是                   | ✗ 否                   |
    | 社会福利          | ✓ 最大化               | ≈ 接近最优（Nash均衡） |
    | 计算复杂度        | 高（需要解VCG支付）    | 低（简单排序）         |
    | 收入              | 不确定                 | 通常更高               |
    | 稳定性            | 可能不稳定             | ✓ 更稳定               |
    | 实际采用          | 少（Overture早期）     | ✓ 广泛（Google等）     |
    | 可预测性          | 难以预测支付           | ✓ 易于理解             |

    为什么实践中使用GSP：
    1. 简单性：广告主容易理解
    2. 稳定性：小变化不会导致大波动
    3. 收入：Nash均衡下收入接近甚至超过VCG
    4. 性能：毫秒级实时竞价
    """

    print(comparison)


if __name__ == '__main__':
    # 运行演示
    demonstrate_gsp_mechanism()

    # 比较机制
    compare_gsp_vcg()

    # 运行测试
    print("\n" + "=" * 60)
    print("运行单元测试")
    print("=" * 60)

    from app01_ad_auction import test
    test()
