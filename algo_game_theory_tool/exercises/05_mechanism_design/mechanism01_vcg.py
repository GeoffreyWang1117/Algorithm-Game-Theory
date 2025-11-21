"""
练习 6: VCG 机制 (Vickrey-Clarke-Groves Mechanism)

VCG 机制是机制设计中最重要的机制之一，它是第二价格拍卖的推广。

VCG 机制的关键思想：
- 每个参与者报告自己的估值 (valuation)
- 机制选择使社会福利最大化的结果
- 每个参与者支付其"外部性"成本 = 其他人因为他参与而损失的福利

VCG 的重要性质：
1. 激励相容：真实报价是占优策略
2. 个体理性：参与者不会亏损（在某些情况下）
3. 社会福利最大化

任务：实现简单的 VCG 机制（单物品拍卖场景）。
"""


def vcg_auction(valuations):
    """
    运行 VCG 拍卖（单物品）

    参数:
        valuations: 估值字典，格式为 {bidder_id: valuation}

    返回:
        tuple: (winner_id, payments)
               payments 是字典 {bidder_id: payment_amount}
    """
    # TODO: 实现 VCG 拍卖
    # 1. 找出估值最高者（获胜者）
    # 2. 计算每个参与者的支付
    #    winner 的支付 = 如果他不参与，其他人能获得的最大社会福利
    #                   - 他参与时，其他人获得的社会福利
    #    对于单物品拍卖，winner 支付第二高的估值
    pass


def vcg_allocation(valuations, items):
    """
    VCG 机制的一般形式：多物品分配

    参数:
        valuations: 每个参与者对每个物品的估值
                   格式为 {bidder_id: {item_id: valuation}}
        items: 可分配的物品列表

    返回:
        tuple: (allocation, payments)
               allocation: {item_id: winner_id}
               payments: {bidder_id: payment_amount}
    """
    # TODO: 实现多物品 VCG 机制
    # 这是一个挑战性的练习！
    # 提示：需要找到最大化社会福利的分配，然后计算 VCG 支付
    pass


def calculate_social_welfare(allocation, valuations):
    """
    计算给定分配的社会福利

    参数:
        allocation: 分配方案 {item_id: bidder_id}
        valuations: 估值 {bidder_id: {item_id: valuation}}

    返回:
        float: 总社会福利
    """
    # TODO: 实现社会福利计算
    # 社会福利 = 所有参与者的估值之和
    pass


# HINT: 对于单物品 VCG 拍卖：
#       winner = argmax(valuations)
#       winner 的支付 = max(其他人的估值)
#       其他人支付 = 0

# HINT: VCG 支付公式：
#       p_i = [max SW without i] - [SW of others with i]
#       其中 SW = social welfare


def test():
    """测试函数"""
    from exercise_runner import Color

    print(f"{Color.CYAN}测试 1: 单物品 VCG 拍卖{Color.END}")

    valuations1 = {
        'Alice': 100,
        'Bob': 80,
        'Charlie': 90
    }

    winner, payments = vcg_auction(valuations1)

    if winner == 'Alice' and payments[winner] == 90:
        print(f"  {Color.GREEN}✓{Color.END} VCG 拍卖正确: {winner} 赢得，支付 {payments[winner]}")
    else:
        print(f"  {Color.RED}✗{Color.END} VCG 拍卖错误")
        print(f"    期望: Alice 赢得，支付 90")
        print(f"    实际: {winner} 赢得，支付 {payments.get(winner, 'N/A')}")
        return False

    # 验证非赢家不支付
    if payments.get('Bob', 0) == 0 and payments.get('Charlie', 0) == 0:
        print(f"  {Color.GREEN}✓{Color.END} 非赢家不支付")
    else:
        print(f"  {Color.RED}✗{Color.END} 非赢家不应该支付")
        return False

    print(f"\n{Color.CYAN}测试 2: VCG 激励相容性{Color.END}")

    # 测试真实报价是最优的
    valuations2 = {
        'Alice': 100,
        'Bob': 95,
        'Charlie': 80
    }

    winner2, payments2 = vcg_auction(valuations2)

    # Alice 的真实估值是 100，她赢得拍卖，支付 95
    # 效用 = 100 - 95 = 5

    if winner2 == 'Alice' and payments2['Alice'] == 95:
        utility_truthful = 100 - payments2['Alice']
        print(f"  {Color.GREEN}✓{Color.END} Alice 真实报价效用: {utility_truthful}")
    else:
        print(f"  {Color.RED}✗{Color.END} VCG 拍卖结果错误")
        return False

    # 如果 Alice 虚报为 90，她会输掉拍卖（Bob 95 > 90）
    # 效用 = 0（输了）
    # 所以真实报价更好：5 > 0
    print(f"  {Color.GREEN}✓{Color.END} 如果 Alice 虚报为 90，她会输掉拍卖（效用=0）")
    print(f"  {Color.GREEN}✓{Color.END} 真实报价是占优策略")

    print(f"\n{Color.CYAN}测试 3: 社会福利最大化{Color.END}")

    valuations3 = {
        'Alice': 100,
        'Bob': 120,  # Bob 估值最高
        'Charlie': 80
    }

    winner3, payments3 = vcg_auction(valuations3)

    if winner3 == 'Bob':
        print(f"  {Color.GREEN}✓{Color.END} 物品分配给估值最高的人（社会福利最大化）")
        print(f"    Bob 支付: {payments3['Bob']}")
    else:
        print(f"  {Color.RED}✗{Color.END} 应该分配给 Bob（估值最高）")
        return False

    return True


if __name__ == '__main__':
    test()
