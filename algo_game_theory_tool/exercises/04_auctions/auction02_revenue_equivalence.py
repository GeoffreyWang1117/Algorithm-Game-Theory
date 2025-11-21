"""
练习 9: 收入等价定理 (Revenue Equivalence Theorem)

收入等价定理是拍卖理论中的重要结果，由 Myerson (1981) 证明。

定理内容：
对于单物品拍卖，假设：
1. 竞标者的估值独立同分布
2. 竞标者是风险中性的
3. 竞标者的估值从同一分布中抽取
4. 支付只依赖于报价

那么，所有满足以下条件的拍卖机制期望收入相同：
- 物品分配给报价最高的竞标者
- 报价为 0 的竞标者期望支付为 0

特别地，第一价格拍卖和第二价格拍卖的期望收入相同！

任务：通过模拟验证第一价格和第二价格拍卖的期望收入。
"""

import random


def first_price_auction(bids):
    """
    第一价格拍卖：最高出价者获胜，支付自己的出价

    参数:
        bids: 报价列表 [(bidder_id, bid), ...]

    返回:
        tuple: (winner_id, price)
    """
    # TODO: 实现第一价格拍卖
    pass


def second_price_auction(bids):
    """
    第二价格拍卖：最高出价者获胜，支付第二高出价

    参数:
        bids: 报价列表 [(bidder_id, bid), ...]

    返回:
        tuple: (winner_id, price)
    """
    # TODO: 实现第二价格拍卖
    pass


def optimal_bid_first_price(valuation, n_competitors, distribution='uniform'):
    """
    计算第一价格拍卖中的最优报价（贝叶斯纳什均衡）

    对于均匀分布 [0, 1] 和 n 个竞标者：
    最优报价 = (n-1)/n * valuation

    参数:
        valuation: 竞标者的真实估值
        n_competitors: 竞争对手数量（不包括自己）
        distribution: 估值分布类型

    返回:
        float: 最优报价
    """
    # TODO: 实现最优报价计算
    # 提示：对于均匀分布，最优报价是 (n-1)/n * valuation
    pass


def simulate_auction_revenue(auction_type, n_bidders, n_simulations=1000):
    """
    模拟拍卖的期望收入

    参数:
        auction_type: 'first' 或 'second'
        n_bidders: 竞标者数量
        n_simulations: 模拟次数

    返回:
        float: 平均收入
    """
    # TODO: 实现拍卖收入模拟
    # 1. 对每次模拟：
    #    - 从均匀分布 [0, 1] 中抽取 n_bidders 个估值
    #    - 根据拍卖类型计算报价
    #      * 第二价格：真实报价
    #      * 第一价格：使用最优报价策略
    #    - 运行拍卖，记录收入
    # 2. 返回平均收入
    pass


# HINT: 收入等价定理说明两种拍卖的期望收入相同
# HINT: 但这需要竞标者使用最优策略！
# HINT: 第二价格拍卖：真实报价是占优策略
# HINT: 第一价格拍卖：最优报价 = (n-1)/n * valuation


def test():
    """测试函数"""
    from exercise_runner import Color

    print(f"{Color.CYAN}测试 1: 第一价格拍卖{Color.END}")

    bids1 = [('Alice', 80), ('Bob', 60), ('Charlie', 70)]
    winner1, price1 = first_price_auction(bids1)

    if winner1 == 'Alice' and price1 == 80:
        print(f"  {Color.GREEN}✓{Color.END} 第一价格拍卖: {winner1} 赢得，支付 {price1}")
    else:
        print(f"  {Color.RED}✗{Color.END} 第一价格拍卖错误")
        return False

    print(f"\n{Color.CYAN}测试 2: 第二价格拍卖{Color.END}")

    bids2 = [('Alice', 80), ('Bob', 60), ('Charlie', 70)]
    winner2, price2 = second_price_auction(bids2)

    if winner2 == 'Alice' and price2 == 70:
        print(f"  {Color.GREEN}✓{Color.END} 第二价格拍卖: {winner2} 赢得，支付 {price2}")
    else:
        print(f"  {Color.RED}✗{Color.END} 第二价格拍卖错误")
        return False

    print(f"\n{Color.CYAN}测试 3: 最优报价计算{Color.END}")

    # 对于 2 个竞标者，最优报价 = 1/2 * valuation
    optimal_bid = optimal_bid_first_price(100, 1, 'uniform')

    if abs(optimal_bid - 50) < 0.1:
        print(f"  {Color.GREEN}✓{Color.END} 最优报价计算正确: {optimal_bid}")
    else:
        print(f"  {Color.RED}✗{Color.END} 最优报价错误，期望 50，得到 {optimal_bid}")
        return False

    # 对于 3 个竞标者，最优报价 = 2/3 * valuation
    optimal_bid_3 = optimal_bid_first_price(90, 2, 'uniform')

    if abs(optimal_bid_3 - 60) < 0.1:
        print(f"  {Color.GREEN}✓{Color.END} 3个竞标者的最优报价: {optimal_bid_3}")
    else:
        print(f"  {Color.RED}✗{Color.END} 最优报价错误")
        return False

    print(f"\n{Color.CYAN}测试 4: 收入等价定理验证（通过模拟）{Color.END}")

    n_bidders = 4
    n_sims = 1000

    revenue_first = simulate_auction_revenue('first', n_bidders, n_sims)
    revenue_second = simulate_auction_revenue('second', n_bidders, n_sims)

    print(f"    第一价格拍卖平均收入: {revenue_first:.4f}")
    print(f"    第二价格拍卖平均收入: {revenue_second:.4f}")
    print(f"    差异: {abs(revenue_first - revenue_second):.4f}")

    # 理论上期望收入应该相同，允许一些模拟误差
    if abs(revenue_first - revenue_second) < 0.05:
        print(f"  {Color.GREEN}✓{Color.END} 收入等价定理得到验证！")
        print(f"  {Color.YELLOW}💡 两种拍卖的期望收入在统计上相同{Color.END}")
    else:
        print(f"  {Color.YELLOW}⚠{Color.END} 差异较大，可能是模拟次数不够")
        # 不算测试失败，因为这是概率性的

    return True


if __name__ == '__main__':
    test()
