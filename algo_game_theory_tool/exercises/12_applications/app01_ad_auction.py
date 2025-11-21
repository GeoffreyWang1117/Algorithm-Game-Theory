"""
练习 20: 广告拍卖系统 (Sponsored Search Auction)

这是算法博弈论最成功的应用之一！Google、Facebook、百度等公司
每年通过广告拍卖产生数千亿美元的收入。

背景：
当用户搜索"买鞋"时，搜索引擎显示相关广告。广告位有限（如3个位置），
但广告主很多。如何分配广告位并定价？

关键概念：
- CTR (Click-Through Rate): 点击率，第1位 > 第2位 > 第3位
- Bid: 广告主愿意为每次点击支付的最高价格
- Quality Score: 广告质量得分（相关性、着陆页质量等）

拍卖机制：
1. **VCG机制**: 理论最优，但复杂
2. **GSP (Generalized Second Price)**: Google实际使用，简单高效
   - 按 bid × quality 排序
   - 广告主i支付：下一位的bid（调整后）

任务：实现一个完整的广告拍卖系统，包括GSP机制和收入计算。
"""

from typing import List, Dict, Tuple


class Advertiser:
    """广告主"""

    def __init__(self, advertiser_id: str, bid: float, quality_score: float):
        """
        初始化广告主

        参数:
            advertiser_id: 广告主ID
            bid: 每次点击出价 (Cost Per Click)
            quality_score: 质量得分 (0-10)
        """
        self.id = advertiser_id
        self.bid = bid
        self.quality_score = quality_score
        self.rank_score = bid * quality_score  # 排名得分


class AdSlot:
    """广告位"""

    def __init__(self, position: int, ctr: float):
        """
        初始化广告位

        参数:
            position: 位置（1是最好）
            ctr: 点击率（基础CTR）
        """
        self.position = position
        self.ctr = ctr


class SponsoredSearchAuction:
    """广告搜索拍卖系统"""

    def __init__(self, slots: List[AdSlot]):
        """
        初始化拍卖系统

        参数:
            slots: 可用的广告位列表
        """
        # TODO: 初始化
        pass

    def run_gsp_auction(self, advertisers: List[Advertiser]) -> Dict:
        """
        运行GSP拍卖

        GSP规则：
        1. 按 bid × quality_score 排序广告主
        2. 分配广告位（得分高的获得好位置）
        3. 计算支付：广告主i支付下一位的"有效bid"
           payment_i = (下一位的rank_score / 自己的quality_score) × 实际CTR

        参数:
            advertisers: 广告主列表

        返回:
            dict: {
                'allocation': {advertiser_id: slot_position},
                'payments': {advertiser_id: total_payment},
                'clicks': {advertiser_id: expected_clicks}
            }
        """
        # TODO: 实现GSP拍卖
        # 1. 按rank_score排序广告主
        # 2. 分配广告位
        # 3. 计算每个广告主的支付和期望点击数
        pass

    def calculate_revenue(self, allocation: Dict, payments: Dict) -> float:
        """
        计算拍卖总收入

        参数:
            allocation: 分配结果
            payments: 支付结果

        返回:
            float: 总收入
        """
        # TODO: 计算总收入
        pass

    def is_truthful_bidding_optimal(self, advertiser: Advertiser,
                                    other_advertisers: List[Advertiser],
                                    true_value_per_click: float) -> bool:
        """
        检查真实出价是否最优（GSP不是激励相容的！）

        参数:
            advertiser: 当前广告主
            other_advertisers: 其他广告主
            true_value_per_click: 真实的每次点击价值

        返回:
            bool: 真实出价是否最优
        """
        # TODO: 检查激励相容性
        # GSP不是激励相容的，存在操纵空间
        pass


# HINT: GSP排序使用 bid × quality_score
# HINT: 支付价格 = (下一位的rank_score) / (自己的quality_score)
# HINT: GSP不是激励相容的（与VCG不同）
# HINT: 但GSP在实践中表现很好（Nash均衡接近VCG）


def test():
    """测试函数"""
    from exercise_runner import Color

    print(f"{Color.CYAN}测试 1: 创建广告拍卖系统{Color.END}")

    # 创建3个广告位，CTR递减
    slots = [
        AdSlot(position=1, ctr=0.10),  # 第1位，10%点击率
        AdSlot(position=2, ctr=0.06),  # 第2位，6%点击率
        AdSlot(position=3, ctr=0.03)   # 第3位，3%点击率
    ]

    auction = SponsoredSearchAuction(slots)
    print(f"  {Color.GREEN}✓{Color.END} 创建了3个广告位")

    print(f"\n{Color.CYAN}测试 2: 广告主竞标{Color.END}")

    advertisers = [
        Advertiser('Nike', bid=5.0, quality_score=9),      # 高质量，中等出价
        Advertiser('Adidas', bid=4.5, quality_score=10),   # 最高质量
        Advertiser('Puma', bid=6.0, quality_score=7),      # 低质量，高出价
        Advertiser('Reebok', bid=3.0, quality_score=8)     # 低出价
    ]

    print(f"  {Color.YELLOW}广告主信息：{Color.END}")
    for adv in advertisers:
        print(f"    {adv.id}: 出价=${adv.bid}, 质量={adv.quality_score}, "
              f"排名得分={adv.rank_score}")

    print(f"\n{Color.CYAN}测试 3: 运行GSP拍卖{Color.END}")

    result = auction.run_gsp_auction(advertisers)

    if result:
        print(f"  {Color.GREEN}✓{Color.END} GSP拍卖完成")
        print(f"\n  {Color.YELLOW}分配结果：{Color.END}")
        for adv_id, position in sorted(result['allocation'].items(),
                                       key=lambda x: x[1]):
            clicks = result['clicks'].get(adv_id, 0)
            payment = result['payments'].get(adv_id, 0)
            cpc = payment / clicks if clicks > 0 else 0
            print(f"    位置{position}: {adv_id}")
            print(f"      - 期望点击: {clicks:.2f}")
            print(f"      - 总支付: ${payment:.2f}")
            print(f"      - 实际CPC: ${cpc:.2f}")
    else:
        print(f"  {Color.RED}✗{Color.END} 请完成GSP拍卖实现")
        return False

    print(f"\n{Color.CYAN}测试 4: 计算平台收入{Color.END}")

    revenue = auction.calculate_revenue(result['allocation'], result['payments'])

    if revenue:
        print(f"  {Color.GREEN}✓{Color.END} 平台总收入: ${revenue:.2f}")
    else:
        print(f"  {Color.YELLOW}提示：完成revenue计算{Color.END}")

    print(f"\n{Color.CYAN}测试 5: GSP vs VCG{Color.END}")

    print(f"  {Color.YELLOW}关键区别：{Color.END}")
    print(f"    VCG (理论最优):")
    print(f"      ✓ 激励相容（真实出价是占优策略）")
    print(f"      ✓ 社会福利最大化")
    print(f"      ✗ 计算复杂")
    print(f"      ✗ 收入可能较低")
    print(f"    ")
    print(f"    GSP (实际使用):")
    print(f"      ✗ 不是激励相容（可被操纵）")
    print(f"      ✓ 简单高效")
    print(f"      ✓ Nash均衡收入接近VCG")
    print(f"      ✓ 更稳定（small changes → small effects）")

    print(f"\n{Color.CYAN}测试 6: 实际应用数据{Color.END}")

    print(f"  {Color.YELLOW}真实世界规模：{Color.END}")
    print(f"    Google AdWords:")
    print(f"      - 每天数十亿次拍卖")
    print(f"      - 数百万广告主")
    print(f"      - 年收入 >$2000亿美元")
    print(f"    ")
    print(f"    关键成功因素:")
    print(f"      1. 质量得分平衡相关性和出价")
    print(f"      2. GSP机制简单可预测")
    print(f"      3. 实时竞价（毫秒级）")
    print(f"      4. 机器学习预测CTR")

    print(f"\n{Color.YELLOW}💡 广告拍卖的影响：{Color.END}")
    print(f"{Color.YELLOW}   - 创造了互联网最大的收入来源{Color.END}")
    print(f"{Color.YELLOW}   - 算法博弈论的最成功应用{Color.END}")
    print(f"{Color.YELLOW}   - 推动了机制设计理论发展{Color.END}")
    print(f"{Color.YELLOW}   - Hal Varian (Google首席经济学家) 的贡献{Color.END}")

    return True


if __name__ == '__main__':
    test()
