"""
练习 24 参考答案: 频谱拍卖

这是app05_spectrum_auction.py的完整参考实现。
"""

from typing import List, Dict, Set, Tuple, Optional
from itertools import combinations, chain


class SpectrumLicense:
    """频谱许可证"""

    def __init__(self, license_id: str, region: str, bandwidth: float,
                 frequency_band: str):
        self.id = license_id
        self.region = region
        self.bandwidth = bandwidth
        self.frequency_band = frequency_band


class Bidder:
    """投标者 - 完整实现"""

    def __init__(self, bidder_id: str, budget: float):
        self.id = bidder_id
        self.budget = budget
        self.valuations = {}

    def add_valuation(self, licenses: Set[str], value: float):
        """添加估值 - 完整实现"""
        self.valuations[frozenset(licenses)] = value

    def get_valuation(self, licenses: Set[str]) -> float:
        """获取估值 - 完整实现"""
        return self.valuations.get(frozenset(licenses), 0.0)


class SynchronousAuction:
    """同步多轮拍卖 - 完整实现"""

    def __init__(self, licenses: List[SpectrumLicense],
                 bidders: List[Bidder],
                 bid_increment: float = 0.1):
        self.licenses = {lic.id: lic for lic in licenses}
        self.bidders = {b.id: b for b in bidders}
        self.bid_increment = bid_increment
        self.current_prices = {lic_id: {'bidder': None, 'price': 0.0}
                              for lic_id in self.licenses}
        self.round = 0

    def submit_bids(self, bids: Dict[str, Dict[str, float]]) -> bool:
        """
        提交一轮出价 - 完整实现
        """
        has_new_bids = False

        for bidder_id, bidder_bids in bids.items():
            for license_id, bid_price in bidder_bids.items():
                if license_id not in self.licenses:
                    continue

                current = self.current_prices[license_id]
                min_bid = current['price'] * (1 + self.bid_increment)

                # 验证出价
                if bid_price >= min_bid and bid_price <= self.bidders[bidder_id].budget:
                    # 接受出价
                    self.current_prices[license_id] = {
                        'bidder': bidder_id,
                        'price': bid_price
                    }
                    has_new_bids = True

        self.round += 1
        return has_new_bids

    def run_auction(self, bidding_strategies: Dict) -> Dict[str, Dict]:
        """
        运行完整拍卖 - 完整实现
        """
        max_rounds = 100  # 防止无限循环

        while self.round < max_rounds:
            # 每个投标者根据当前价格决定出价
            round_bids = {}

            for bidder_id, strategy in bidding_strategies.items():
                bidder = self.bidders[bidder_id]
                bids = strategy(bidder, self.current_prices, self.licenses)
                if bids:
                    round_bids[bidder_id] = bids

            # 提交出价
            has_new = self.submit_bids(round_bids)

            if not has_new:
                # 没有新出价，拍卖结束
                break

        # 确定最终分配和支付
        allocations = {}
        payments = {}

        for license_id, result in self.current_prices.items():
            if result['bidder'] is not None:
                bidder_id = result['bidder']
                if bidder_id not in allocations:
                    allocations[bidder_id] = []
                    payments[bidder_id] = 0.0

                allocations[bidder_id].append(license_id)
                payments[bidder_id] += result['price']

        return {
            'allocations': allocations,
            'payments': payments,
            'rounds': self.round
        }


def simple_bidding_strategy(bidder: Bidder, current_prices: Dict,
                           licenses: Dict) -> Dict[str, float]:
    """
    简单出价策略 - 完整实现
    """
    bids = {}

    for license_id in licenses:
        # 单个许可证的估值
        valuation = bidder.get_valuation({license_id})
        current_price = current_prices[license_id]['price']

        # 如果估值高于当前价格，出价
        min_bid = current_price * 1.1  # 10% 增量

        if valuation > min_bid:
            # 出价略高于最低要求
            bid_price = min(min_bid, valuation * 0.9)  # 不超过估值的90%
            bids[license_id] = bid_price

    return bids


def package_bidding_strategy(bidder: Bidder, current_prices: Dict,
                            desired_package: Set[str]) -> Dict[str, float]:
    """
    包裹出价策略 - 完整实现
    """
    # 计算包裹的总估值和总成本
    package_valuation = bidder.get_valuation(desired_package)

    total_current_cost = sum(current_prices[lic_id]['price']
                            for lic_id in desired_package)

    min_total_bid = total_current_cost * 1.1  # 10% 增量

    # 只有当包裹估值高于总成本时才出价
    if package_valuation > min_total_bid:
        # 均匀分配出价到各个许可证
        bid_per_license = min_total_bid / len(desired_package)

        bids = {lic_id: bid_per_license for lic_id in desired_package}
        return bids

    return {}


class CombinatorialAuction:
    """组合拍卖 - 完整实现"""

    def __init__(self, licenses: List[SpectrumLicense],
                 bidders: List[Bidder]):
        self.licenses = {lic.id: lic for lic in licenses}
        self.bidders = {b.id: b for b in bidders}
        self.package_bids = []

    def submit_package_bid(self, bidder_id: str, licenses: Set[str],
                          bid_price: float):
        """提交包裹出价 - 完整实现"""
        self.package_bids.append((bidder_id, frozenset(licenses), bid_price))

    def solve_winner_determination(self) -> Dict:
        """
        赢家确定问题 - 完整实现

        简化版本：枚举所有可行分配
        实际应用：使用整数规划求解器（如CPLEX）
        """
        if not self.package_bids:
            return {'allocation': {}, 'revenue': 0.0}

        best_allocation = {}
        best_revenue = 0.0

        # 生成所有可能的包裹组合
        n_bids = len(self.package_bids)

        # 枚举所有子集
        for r in range(n_bids + 1):
            for bid_subset in combinations(range(n_bids), r):
                # 检查这个子集是否可行（没有许可证冲突）
                allocation = {}
                revenue = 0.0
                used_licenses = set()
                is_feasible = True

                for bid_idx in bid_subset:
                    bidder_id, licenses, price = self.package_bids[bid_idx]

                    # 检查许可证冲突
                    if used_licenses & licenses:
                        is_feasible = False
                        break

                    used_licenses |= licenses
                    if bidder_id not in allocation:
                        allocation[bidder_id] = set()
                    allocation[bidder_id] |= licenses
                    revenue += price

                if is_feasible and revenue > best_revenue:
                    best_revenue = revenue
                    best_allocation = allocation

        return {
            'allocation': best_allocation,
            'revenue': best_revenue
        }


def analyze_complementarity(bidder: Bidder, licenses: List[str]) -> float:
    """
    分析互补性 - 完整实现
    """
    if len(licenses) < 2:
        return 0.0

    # 组合估值
    combined_value = bidder.get_valuation(set(licenses))

    # 单个估值之和
    individual_sum = sum(bidder.get_valuation({lic}) for lic in licenses)

    if individual_sum == 0:
        return 0.0

    # 互补性系数
    complementarity = (combined_value / individual_sum) - 1

    return complementarity


def check_exposure_problem(bidder: Bidder, won_licenses: Set[str],
                          desired_package: Set[str]) -> bool:
    """
    检查曝光问题 - 完整实现
    """
    # 必须是真子集
    if not (won_licenses < desired_package):
        return False

    # 部分包裹的价值
    partial_value = bidder.get_valuation(won_licenses)

    # 如果部分价值明显低于期望
    # 这里简化：如果部分价值 < 完整包裹价值的一半
    full_value = bidder.get_valuation(desired_package)

    return partial_value < full_value * 0.5


def vcg_pricing_spectrum(allocation: Dict[str, Set[str]],
                        all_bids: List[Tuple],
                        licenses: Set[str]) -> Dict[str, float]:
    """
    VCG定价 - 完整实现
    """
    payments = {}

    for winner_id in allocation:
        # 计算没有这个赢家时的最优收入
        # 简化实现：重新运行WDP，排除该赢家的出价

        # 过滤出价
        bids_without_winner = [
            (bidder, lics, price) for bidder, lics, price in all_bids
            if bidder != winner_id
        ]

        # 创建临时组合拍卖
        temp_auction = CombinatorialAuction([], [])
        temp_auction.package_bids = [
            (bidder, lics, price) for bidder, lics, price in bids_without_winner
        ]

        # 求解
        result_without = temp_auction.solve_winner_determination()
        revenue_without = result_without['revenue']

        # 其他赢家在当前分配中的收入
        revenue_others = sum(
            price for bidder, lics, price in all_bids
            if bidder in allocation and bidder != winner_id
        )

        # VCG支付
        payment = revenue_without - revenue_others
        payments[winner_id] = max(0, payment)  # 不能是负数

    return payments


def demonstrate_fcc_auction():
    """演示FCC频谱拍卖案例"""
    print("=" * 70)
    print("FCC Auction 73 (700MHz) 案例研究")
    print("=" * 70)

    # 创建许可证
    licenses = [
        SpectrumLicense('A-Block-1', 'Northeast', 12, '700MHz'),
        SpectrumLicense('A-Block-2', 'Southeast', 12, '700MHz'),
        SpectrumLicense('A-Block-3', 'West', 12, '700MHz'),
        SpectrumLicense('B-Block', 'National', 22, '700MHz'),
        SpectrumLicense('C-Block', 'National', 22, '700MHz'),
    ]

    print("\n许可证列表：")
    print("-" * 70)
    for lic in licenses:
        print(f"  {lic.id:20s}: {lic.region:15s} {lic.bandwidth}MHz")

    # 创建投标者
    att = Bidder('AT&T', budget=10000)
    verizon = Bidder('Verizon', budget=12000)
    google = Bidder('Google', budget=5000)

    # 设置估值（展示互补性）
    # AT&T 偏好区域覆盖
    att.add_valuation({'A-Block-1'}, 1000)
    att.add_valuation({'A-Block-2'}, 1000)
    att.add_valuation({'A-Block-3'}, 1000)
    att.add_valuation({'A-Block-1', 'A-Block-2', 'A-Block-3'}, 4000)  # 互补性

    # Verizon 偏好全国性许可证
    verizon.add_valuation({'C-Block'}, 9400)
    verizon.add_valuation({'B-Block'}, 6600)

    # Google 试探性参与
    google.add_valuation({'C-Block'}, 4700)  # 开放接入要求的底价

    print("\n投标者估值：")
    print("-" * 70)
    print(f"  AT&T:")
    print(f"    单个A-Block: $1000M")
    print(f"    全部3个A-Block: $4000M（互补性！）")
    print(f"  Verizon:")
    print(f"    C-Block (全国): $9400M")
    print(f"    B-Block (全国): $6600M")
    print(f"  Google:")
    print(f"    C-Block: $4700M（战略性出价，推高价格）")

    # 分析互补性
    complementarity = analyze_complementarity(
        att, ['A-Block-1', 'A-Block-2', 'A-Block-3']
    )

    print(f"\nAT&T的互补性分析：")
    print(f"  互补性系数: {complementarity:.2%}")
    print(f"  解释: 组合价值比单独价值之和高 {complementarity:.0%}")

    # 运行组合拍卖
    auction = CombinatorialAuction(licenses, [att, verizon, google])

    # 提交包裹出价
    auction.submit_package_bid('AT&T', {'A-Block-1', 'A-Block-2', 'A-Block-3'}, 4000)
    auction.submit_package_bid('Verizon', {'C-Block'}, 9400)
    auction.submit_package_bid('Verizon', {'B-Block'}, 6600)
    auction.submit_package_bid('Google', {'C-Block'}, 4700)

    print("\n拍卖结果：")
    print("-" * 70)

    result = auction.solve_winner_determination()

    for bidder_id, won_licenses in result['allocation'].items():
        print(f"  {bidder_id}: {', '.join(won_licenses)}")

    print(f"\n总收入: ${result['revenue']:.0f}M")

    print("\n历史对比：")
    print("-" * 70)
    print(f"  实际FCC Auction 73总收入: $19,600M")
    print(f"  本模拟收入: ${result['revenue']:.0f}M")
    print(f"  （简化模型，仅供演示）")


def demonstrate_incentive_auction():
    """演示激励拍卖（双向拍卖）"""
    print("\n" + "=" * 70)
    print("FCC Incentive Auction (2017) 案例")
    print("=" * 70)

    print("\n双向拍卖机制：")
    print("-" * 70)

    # 反向拍卖：电视台出售频谱
    print("\n反向拍卖（电视台）：")
    tv_stations = {
        'ABC': {'willing_to_sell': True, 'asking_price': 500},
        'NBC': {'willing_to_sell': True, 'asking_price': 450},
        'CBS': {'willing_to_sell': True, 'asking_price': 550},
        'FOX': {'willing_to_sell': False, 'asking_price': float('inf')},
    }

    for station, info in tv_stations.items():
        if info['willing_to_sell']:
            print(f"  {station}: 愿意以 ${info['asking_price']}M 出售")
        else:
            print(f"  {station}: 不愿出售")

    # 选择最低价的几个
    sellers = sorted(
        [(s, info['asking_price']) for s, info in tv_stations.items()
         if info['willing_to_sell']],
        key=lambda x: x[1]
    )[:2]  # 选择2个最便宜的

    reverse_cost = sum(price for _, price in sellers)

    print(f"\n反向拍卖结果：")
    print(f"  购买频谱from: {', '.join(s for s, _ in sellers)}")
    print(f"  总成本: ${reverse_cost}M")

    # 正向拍卖：移动运营商购买
    print("\n正向拍卖（移动运营商）：")

    mobile_bids = {
        'AT&T': 600,
        'Verizon': 700,
        'T-Mobile': 500,
    }

    for operator, bid in mobile_bids.items():
        print(f"  {operator}: ${bid}M")

    # 选择最高价的几个
    buyers = sorted(mobile_bids.items(), key=lambda x: x[1], reverse=True)[:2]

    forward_revenue = sum(bid for _, bid in buyers)

    print(f"\n正向拍卖结果：")
    print(f"  获胜者: {', '.join(b for b, _ in buyers)}")
    print(f"  总收入: ${forward_revenue}M")

    # 匹配结果
    print(f"\n双向拍卖结算：")
    print("-" * 70)
    print(f"  正向收入: ${forward_revenue}M")
    print(f"  反向成本: ${reverse_cost}M")
    print(f"  政府净收入: ${forward_revenue - reverse_cost}M")

    if forward_revenue >= reverse_cost:
        print(f"  {' ✓ 拍卖成功！'}")
    else:
        print(f"  ✗ 拍卖失败（收入不足以覆盖成本）")

    print("\n实际结果对比：")
    print("-" * 70)
    print(f"  实际正向收入: $19,800M")
    print(f"  实际反向成本: $10,000M")
    print(f"  实际政府净收入: $9,800M")


if __name__ == '__main__':
    # 运行演示
    demonstrate_fcc_auction()
    demonstrate_incentive_auction()

    # 运行测试
    print("\n" + "=" * 70)
    print("运行单元测试")
    print("=" * 70)

    from app05_spectrum_auction import test
    test()
