"""
练习 24: 频谱拍卖 (Spectrum Auction)

频谱拍卖是拍卖理论最成功的应用之一，涉及数十亿美元的交易。

背景：
- 无线电频谱是稀缺资源（用于手机、WiFi、广播等）
- 政府（如 FCC）通过拍卖分配频谱许可证
- 传统方法（抽签、听证会）效率低下
- 拍卖机制确保频谱分配给最有价值的使用者

频谱拍卖的特殊挑战：
1. 组合拍卖：投标者对频谱组合有偏好
   - 例如：全国覆盖需要多个区域的频谱
   - 互补性：A+B 的价值 > A的价值 + B的价值

2. 曝光问题（Exposure Problem）：
   - 投标者赢得部分组合可能遭受损失
   - 例如：需要A和B，但只赢得A

3. 免费骑乘（Free Riding）：
   - 等待其他人出价，然后在最后时刻加入

4. 共谋（Collusion）：
   - 投标者可能串通压低价格

真实案例：
- FCC 频谱拍卖（美国）：自1994年以来筹集超过$2000亿
- 3G/4G/5G 频谱拍卖（全球）：数百亿美元
- 2017年激励拍卖：双向拍卖，从电视台回收频谱

拍卖格式：
1. 同步多轮拍卖（SMR - Simultaneous Multiple Round）
2. 组合时钟拍卖（CCA - Combinatorial Clock Auction）
3. 激励拍卖（Incentive Auction）：双向拍卖

任务：实现并分析频谱拍卖机制。
"""

from typing import List, Dict, Set, Tuple, Optional
from itertools import combinations


class SpectrumLicense:
    """频谱许可证"""

    def __init__(self, license_id: str, region: str, bandwidth: float,
                 frequency_band: str):
        """
        初始化频谱许可证

        参数:
            license_id: 许可证ID
            region: 地理区域（如 "Northeast", "California"）
            bandwidth: 带宽（MHz）
            frequency_band: 频段（如 "700MHz", "2.5GHz"）
        """
        self.id = license_id
        self.region = region
        self.bandwidth = bandwidth
        self.frequency_band = frequency_band


class Bidder:
    """投标者（如电信运营商）"""

    def __init__(self, bidder_id: str, budget: float):
        """
        初始化投标者

        参数:
            bidder_id: 投标者ID
            budget: 预算上限
        """
        self.id = bidder_id
        self.budget = budget
        # 对许可证组合的估值
        # {frozenset(license_ids): value}
        self.valuations = {}

    def add_valuation(self, licenses: Set[str], value: float):
        """
        添加对许可证组合的估值

        参数:
            licenses: 许可证ID集合
            value: 估值
        """
        # TODO: 添加估值
        # 使用 frozenset 以便作为字典键
        pass

    def get_valuation(self, licenses: Set[str]) -> float:
        """
        获取对许可证组合的估值

        参数:
            licenses: 许可证ID集合

        返回:
            float: 估值（如果未指定，返回0）
        """
        # TODO: 获取估值
        pass


class SynchronousAuction:
    """同步多轮拍卖（SMR）"""

    def __init__(self, licenses: List[SpectrumLicense],
                 bidders: List[Bidder],
                 bid_increment: float = 0.1):
        """
        初始化同步拍卖

        参数:
            licenses: 许可证列表
            bidders: 投标者列表
            bid_increment: 最小加价幅度（0.1 = 10%）
        """
        self.licenses = {lic.id: lic for lic in licenses}
        self.bidders = {b.id: b for b in bidders}
        self.bid_increment = bid_increment

        # 当前每个许可证的最高出价
        # {license_id: {'bidder': bidder_id, 'price': price}}
        self.current_prices = {lic_id: {'bidder': None, 'price': 0.0}
                              for lic_id in self.licenses}

        # 拍卖轮次
        self.round = 0

    def submit_bids(self, bids: Dict[str, Dict[str, float]]) -> bool:
        """
        提交一轮出价

        参数:
            bids: {bidder_id: {license_id: bid_price}}

        返回:
            bool: 是否有新的有效出价
        """
        # TODO: 处理出价
        # 1. 验证出价（大于当前价格 + 增量）
        # 2. 更新 current_prices
        # 3. 如果有新出价，返回 True
        pass

    def run_auction(self, bidding_strategies: Dict) -> Dict[str, Dict]:
        """
        运行完整拍卖

        参数:
            bidding_strategies: 投标者的出价策略函数
                               {bidder_id: strategy_function}

        返回:
            dict: 拍卖结果 {'allocations': {...}, 'payments': {...}}
        """
        # TODO: 运行拍卖
        # 1. 循环运行拍卖轮次
        # 2. 每轮调用投标者策略获取出价
        # 3. 直到没有新出价
        # 4. 返回最终分配和支付
        pass


def simple_bidding_strategy(bidder: Bidder, current_prices: Dict,
                           licenses: Dict) -> Dict[str, float]:
    """
    简单出价策略：对估值高于当前价格的许可证出价

    参数:
        bidder: 投标者
        current_prices: 当前价格
        licenses: 许可证信息

    返回:
        dict: {license_id: bid_price}
    """
    # TODO: 实现简单策略
    # 对每个许可证，如果 valuation > current_price，出价
    pass


def package_bidding_strategy(bidder: Bidder, current_prices: Dict,
                            desired_package: Set[str]) -> Dict[str, float]:
    """
    包裹出价策略：只对完整包裹出价（避免曝光问题）

    参数:
        bidder: 投标者
        current_prices: 当前价格
        desired_package: 期望的许可证包裹

    返回:
        dict: {license_id: bid_price}
    """
    # TODO: 实现包裹策略
    # 计算整个包裹的总成本
    # 只有当总成本 < 包裹估值时才出价
    pass


class CombinatorialAuction:
    """组合拍卖（允许对组合出价）"""

    def __init__(self, licenses: List[SpectrumLicense],
                 bidders: List[Bidder]):
        """
        初始化组合拍卖

        参数:
            licenses: 许可证列表
            bidders: 投标者列表
        """
        self.licenses = {lic.id: lic for lic in licenses}
        self.bidders = {b.id: b for b in bidders}

        # 所有提交的包裹出价
        # [(bidder_id, license_set, bid_price), ...]
        self.package_bids = []

    def submit_package_bid(self, bidder_id: str, licenses: Set[str],
                          bid_price: float):
        """
        提交包裹出价

        参数:
            bidder_id: 投标者ID
            licenses: 许可证集合
            bid_price: 出价
        """
        # TODO: 添加包裹出价
        pass

    def solve_winner_determination(self) -> Dict:
        """
        赢家确定问题（Winner Determination Problem, WDP）

        目标：最大化总收入，使得每个许可证最多分配给一个投标者

        这是一个NP-hard问题（类似于加权集合打包问题）

        返回:
            dict: {'allocation': {bidder_id: set(license_ids)},
                   'revenue': total_revenue}
        """
        # TODO: 实现赢家确定
        # 简化实现：枚举所有可行分配，选择收入最高的
        # 实际应用：使用整数规划求解器
        pass


def analyze_complementarity(bidder: Bidder, licenses: List[str]) -> float:
    """
    分析许可证之间的互补性

    参数:
        bidder: 投标者
        licenses: 许可证列表

    返回:
        float: 互补性系数
               = 组合估值 / 单个估值之和 - 1
               > 0 表示互补，< 0 表示替代
    """
    # TODO: 计算互补性
    # complementarity = V(A ∪ B) / [V(A) + V(B)] - 1
    pass


def check_exposure_problem(bidder: Bidder, won_licenses: Set[str],
                          desired_package: Set[str]) -> bool:
    """
    检查是否存在曝光问题

    投标者赢得部分包裹，但价值低于支付

    参数:
        bidder: 投标者
        won_licenses: 赢得的许可证
        desired_package: 期望的完整包裹

    返回:
        bool: 是否存在曝光问题
    """
    # TODO: 检查曝光问题
    # 如果 won_licenses ⊂ desired_package（真子集）
    # 且 V(won_licenses) < payment(won_licenses)
    # 则存在曝光问题
    pass


def vcg_pricing_spectrum(allocation: Dict[str, Set[str]],
                        all_bids: List[Tuple],
                        licenses: Set[str]) -> Dict[str, float]:
    """
    VCG定价用于频谱拍卖

    每个赢家支付其"社会成本"：
    payment_i = (其他人在没有i时的最优收入) - (其他人在有i时的收入)

    参数:
        allocation: 最优分配 {bidder_id: set(licenses)}
        all_bids: 所有出价 [(bidder_id, licenses, bid_price), ...]
        licenses: 所有许可证

    返回:
        dict: {bidder_id: payment}
    """
    # TODO: 实现VCG定价
    pass


# HINT: 组合拍卖的赢家确定是NP-hard问题
# HINT: 曝光问题是真实拍卖中的重要关切
# HINT: VCG在组合拍卖中可能导致低收入
# HINT: 实际FCC拍卖使用同步多轮 + 组合时钟混合格式


def test():
    """测试函数"""
    from exercise_runner import Color

    print(f"{Color.CYAN}测试 1: 创建频谱许可证{Color.END}")

    licenses = [
        SpectrumLicense('L1', 'Northeast', 10, '700MHz'),
        SpectrumLicense('L2', 'Southeast', 10, '700MHz'),
        SpectrumLicense('L3', 'West', 10, '700MHz'),
    ]

    print(f"  {Color.GREEN}✓{Color.END} 创建了3个许可证")
    for lic in licenses:
        print(f"    {lic.id}: {lic.region}, {lic.bandwidth}MHz, {lic.frequency_band}")

    print(f"\n{Color.CYAN}测试 2: 投标者估值（互补性）{Color.END}")

    # 电信运营商想要全国覆盖
    bidder1 = Bidder('AT&T', budget=1000)

    print(f"  {Color.YELLOW}估值示例：{Color.END}")
    print(f"    L1 单独: $100M")
    print(f"    L2 单独: $100M")
    print(f"    L1+L2 组合: $250M（互补性！）")
    print(f"  ")
    print(f"    互补性系数 = 250/(100+100) - 1 = 0.25")
    print(f"    {Color.GREEN}组合价值 > 单独价值之和{Color.END}")

    print(f"\n{Color.CYAN}测试 3: 曝光问题演示{Color.END}")

    print(f"  {Color.YELLOW}场景：{Color.END}")
    print(f"    投标者想要 L1+L2 组合（估值 $250M）")
    print(f"    L1 出价 $130M，L2 出价 $130M")
    print(f"  ")
    print(f"    情况1：赢得 L1+L2")
    print(f"      价值: $250M")
    print(f"      支付: $260M")
    print(f"      利润: -$10M")
    print(f"  ")
    print(f"    情况2：只赢得 L1（曝光！）")
    print(f"      价值: $100M（L1单独）")
    print(f"      支付: $130M")
    print(f"      利润: -$30M（损失更大！）")
    print(f"  ")
    print(f"    {Color.RED}这就是曝光问题：部分赢得比全输更糟！{Color.END}")

    print(f"\n{Color.CYAN}测试 4: 同步多轮拍卖{Color.END}")

    print(f"  {Color.YELLOW}SMR 拍卖流程：{Color.END}")
    print(f"    第1轮: 所有许可证同时开始，底价 $0")
    print(f"      AT&T 对 L1 出价 $100M")
    print(f"      Verizon 对 L1 出价 $110M")
    print(f"  ")
    print(f"    第2轮: L1 当前价格 $110M")
    print(f"      AT&T 对 L1 出价 $120M")
    print(f"  ")
    print(f"    第3轮: 无新出价")
    print(f"      拍卖结束")
    print(f"  ")
    print(f"    {Color.GREEN}✓ AT&T 赢得 L1，支付 $120M{Color.END}")

    print(f"\n{Color.CYAN}测试 5: 组合拍卖{Color.END}")

    print(f"  {Color.YELLOW}组合拍卖优势：{Color.END}")
    print(f"    允许对许可证包裹出价")
    print(f"    避免曝光问题")
    print(f"  ")
    print(f"    示例出价：")
    print(f"      AT&T: {{L1, L2}} → $250M")
    print(f"      Verizon: {{L1}} → $110M, {{L2}} → $110M")
    print(f"  ")
    print(f"    赢家确定问题（WDP）：")
    print(f"      选项1: AT&T 获得 {{L1, L2}} → 收入 $250M")
    print(f"      选项2: Verizon 获得 L1 和 L2 → 收入 $220M")
    print(f"  ")
    print(f"    {Color.GREEN}✓ 选择选项1，收入更高{Color.END}")

    print(f"\n{Color.CYAN}测试 6: 真实案例 - FCC 频谱拍卖{Color.END}")

    print(f"  {Color.YELLOW}FCC Auction 73 (700MHz, 2008):{Color.END}")
    print(f"    背景: 数字电视转换，释放 700MHz 频谱")
    print(f"    参与者: AT&T, Verizon, Google, 等")
    print(f"    格式: 同步多轮拍卖")
    print(f"    总收入: $19.6 billion")
    print(f"  ")
    print(f"    关键结果:")
    print(f"      - Verizon 赢得 C-Block（全国性）: $9.4B")
    print(f"      - AT&T 赢得 B-Block: $6.6B")
    print(f"      - 拍卖持续 38 天，261 轮")
    print(f"  ")
    print(f"    {Color.GREEN}拍卖理论的胜利！{Color.END}")

    print(f"\n{Color.CYAN}测试 7: 激励拍卖（双向拍卖）{Color.END}")

    print(f"  {Color.YELLOW}FCC Incentive Auction (2017):{Color.END}")
    print(f"    目标: 从电视台回收频谱，转给移动运营商")
    print(f"  ")
    print(f"    两个拍卖：")
    print(f"      1. 反向拍卖: 电视台出售频谱许可")
    print(f"         电视台报价越低越好（想要出售）")
    print(f"  ")
    print(f"      2. 正向拍卖: 移动运营商购买频谱")
    print(f"         运营商出价越高越好（想要购买）")
    print(f"  ")
    print(f"    机制:")
    print(f"      - 运行反向拍卖获得供给")
    print(f"      - 运行正向拍卖获得需求")
    print(f"      - 如果 正向收入 ≥ 反向支出，成功！")
    print(f"  ")
    print(f"    结果:")
    print(f"      - 释放 84MHz 频谱")
    print(f"      - 支付电视台: $10B")
    print(f"      - 移动运营商支付: $19.8B")
    print(f"      - 政府净收入: $9.8B")
    print(f"  ")
    print(f"      {Color.GREEN}✓ 双向拍卖成功！{Color.END}")

    print(f"\n{Color.CYAN}测试 8: 拍卖设计的权衡{Color.END}")

    print(f"  {Color.YELLOW}设计考虑：{Color.END}")
    print(f"  ")
    print(f"    1. 效率 vs 收入")
    print(f"       - VCG: 高效率，但可能低收入")
    print(f"       - 第一价格: 高收入，但可能低效")
    print(f"  ")
    print(f"    2. 简单性 vs 表达能力")
    print(f"       - 同步拍卖: 简单，但有曝光问题")
    print(f"       - 组合拍卖: 表达力强，但WDP是NP-hard")
    print(f"  ")
    print(f"    3. 速度 vs 价格发现")
    print(f"       - 封闭式: 快速，但信息少")
    print(f"       - 多轮: 慢，但价格发现好")
    print(f"  ")
    print(f"    {Color.RED}没有完美的拍卖设计！{Color.END}")

    print(f"\n{Color.YELLOW}💡 频谱拍卖的启示：{Color.END}")
    print(f"{Color.YELLOW}   - 拍卖理论最成功的实际应用（$2000亿+）{Color.END}")
    print(f"{Color.YELLOW}   - 组合拍卖解决互补性问题{Color.END}")
    print(f"{Color.YELLOW}   - 机制设计需要权衡多个目标{Color.END}")
    print(f"{Color.YELLOW}   - 应用：电力市场、碳排放权、公共资源分配{Color.END}")

    return True


if __name__ == '__main__':
    test()
