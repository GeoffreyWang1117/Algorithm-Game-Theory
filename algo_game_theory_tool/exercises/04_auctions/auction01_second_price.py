"""
练习 5: 第二价格密封拍卖 (Second-Price Sealed-Bid Auction / Vickrey Auction)

第二价格拍卖是由 William Vickrey 提出的著名拍卖机制：
- 所有竞标者同时提交密封的报价
- 出价最高者获胜
- 但只需支付第二高的报价

关键性质（Vickrey 定理）：
1. 激励相容 (Incentive Compatible)：真实报价是占优策略
2. 个体理性 (Individual Rational)：参与者不会亏损
3. 帕累托有效 (Pareto Efficient)：物品分配给估值最高的人

任务：实现第二价格拍卖机制，并验证真实报价是占优策略。
"""


def second_price_auction(bids):
    """
    运行第二价格拍卖

    参数:
        bids: 报价列表，格式为 [(bidder_id, bid_amount), ...]

    返回:
        tuple: (winner_id, price_paid) 获胜者和支付价格
               如果没有出价则返回 (None, 0)
    """
    # TODO: 实现第二价格拍卖逻辑
    pass


def calculate_utility(valuation, bid, others_bids):
    """
    计算竞标者在第二价格拍卖中的效用

    参数:
        valuation: 竞标者对物品的真实估值
        bid: 竞标者的报价
        others_bids: 其他竞标者的报价列表

    返回:
        float: 竞标者的效用
               如果赢得拍卖: valuation - second_highest_price
               否则: 0
    """
    # TODO: 实现效用计算
    pass


def verify_truthful_dominant(valuation, others_bids):
    """
    验证在第二价格拍卖中，真实报价是占优策略

    参数:
        valuation: 竞标者的真实估值
        others_bids: 其他竞标者的报价列表

    返回:
        bool: True 如果真实报价的效用 >= 任何其他报价的效用
    """
    # TODO: 验证真实报价是占优策略
    # 提示：比较真实报价和其他可能报价的效用
    pass


# HINT: 第二价格拍卖中，winner = argmax(bids), price = second_max(bids)
# HINT: 效用 = (估值 - 支付价格) if 获胜 else 0
# HINT: 验证占优策略：对于任何 others_bids，u(真实报价) >= u(其他报价)


def test():
    """测试函数"""
    from exercise_runner import Color

    print(f"{Color.CYAN}测试 1: 基本第二价格拍卖{Color.END}")

    bids1 = [('Alice', 100), ('Bob', 80), ('Charlie', 90)]
    winner, price = second_price_auction(bids1)

    if winner == 'Alice' and price == 90:
        print(f"  {Color.GREEN}✓{Color.END} 拍卖结果正确: {winner} 赢得拍卖，支付 {price}")
    else:
        print(f"  {Color.RED}✗{Color.END} 错误: 应该是 Alice 赢得，支付 90")
        print(f"    实际: {winner} 赢得，支付 {price}")
        return False

    print(f"\n{Color.CYAN}测试 2: 效用计算{Color.END}")

    # Alice 估值 100，报价 100，其他人最高报价 90
    utility_win = calculate_utility(100, 100, [80, 90])
    # Bob 估值 80，报价 80，输了
    utility_lose = calculate_utility(80, 80, [100, 90])

    if abs(utility_win - 10) < 0.001 and abs(utility_lose - 0) < 0.001:
        print(f"  {Color.GREEN}✓{Color.END} 效用计算正确")
        print(f"    获胜者效用: {utility_win}")
        print(f"    失败者效用: {utility_lose}")
    else:
        print(f"  {Color.RED}✗{Color.END} 效用计算错误")
        print(f"    期望: 获胜者=10, 失败者=0")
        print(f"    实际: 获胜者={utility_win}, 失败者={utility_lose}")
        return False

    print(f"\n{Color.CYAN}测试 3: 验证真实报价是占优策略{Color.END}")

    # 测试几种情况
    test_cases = [
        (100, [80, 90], "估值高于所有其他报价"),
        (85, [80, 90], "估值在中间"),
        (70, [80, 90], "估值低于所有其他报价"),
    ]

    all_passed = True
    for valuation, others, description in test_cases:
        is_dominant = verify_truthful_dominant(valuation, others)
        if is_dominant:
            print(f"  {Color.GREEN}✓{Color.END} {description}: 真实报价是占优策略")
        else:
            print(f"  {Color.RED}✗{Color.END} {description}: 验证失败")
            all_passed = False

    if not all_passed:
        return False

    print(f"\n{Color.CYAN}测试 4: 对比非真实报价{Color.END}")

    # 演示虚报的后果
    valuation = 100
    others = [80, 90]

    # 真实报价
    utility_truthful = calculate_utility(valuation, valuation, others)
    # 虚高报价
    utility_overbid = calculate_utility(valuation, 110, others)
    # 虚低报价（输掉拍卖）
    utility_underbid = calculate_utility(valuation, 85, others)

    print(f"    真实报价 (100) 效用: {utility_truthful}")
    print(f"    虚高报价 (110) 效用: {utility_overbid}")
    print(f"    虚低报价 (85) 效用: {utility_underbid}")

    # 真实报价应该不劣于虚低报价
    if utility_truthful >= utility_underbid - 0.001:
        print(f"  {Color.GREEN}✓{Color.END} 真实报价优于或等于虚低报价")
    else:
        print(f"  {Color.RED}✗{Color.END} 真实报价应该优于虚低报价")
        return False

    return True


if __name__ == '__main__':
    test()
