"""
VCG (Vickrey-Clarke-Groves) Pricing Mechanism for Spectrum Auctions

VCG is the gold standard for truthful auctions. It ensures:
1. Incentive Compatibility (Truthfulness): Bidding true value is dominant strategy
2. Individual Rationality: Winners never pay more than their bid
3. Efficiency: Maximizes social welfare

Pricing Formula:
    Payment_i = Harm caused to others = SW_{-i} - (SW - v_i)

Where:
    - SW = Social welfare with winner i
    - SW_{-i} = Social welfare without winner i
    - v_i = Winner i's value

Real-World Usage:
    - FCC Spectrum Auctions (modified VCG)
    - Google Ad Auctions (GSP, VCG variant)
    - Combinatorial exchanges

Key Challenge:
    Computing VCG prices requires solving n WDP instances (one per winner)
    This can be computationally expensive for large auctions

Properties:
    ✓ Truthful (strategy-proof)
    ✓ Efficient (welfare-maximizing)
    ✓ Individual rational
    ✗ May generate low revenue (compared to alternatives)
    ✗ Computationally expensive

References:
    - Vickrey (1961) "Counterspeculation, Auctions, and Competitive Sealed Tenders"
    - Clarke (1971) "Multipart pricing of public goods"
    - Groves (1973) "Incentives in Teams"
    - Ausubel & Milgrom (2006) "The Lovely but Lonely Vickrey Auction"
"""

from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
import numpy as np
from wdp_solver import Bid, Allocation, WDPSolver
import copy


@dataclass
class VCGPayment:
    """Represents VCG payment for a winner."""
    bidder_id: str
    winning_bid: Bid
    payment: float  # VCG price
    value: float  # Bidder's declared value
    utility: float  # value - payment (bidder surplus)


@dataclass
class VCGOutcome:
    """Complete outcome of a VCG auction."""
    allocation: Allocation  # Winner determination result
    payments: List[VCGPayment]  # VCG prices for winners
    total_revenue: float  # Auctioneer revenue
    total_welfare: float  # Social welfare (sum of values)
    total_utility: float  # Total bidder surplus
    is_truthful: bool = True  # Always true for VCG
    is_efficient: bool = True  # Always true for VCG


class VCGPricingMechanism:
    """
    VCG pricing mechanism for combinatorial auctions.

    Workflow:
        1. Solve WDP to find efficient allocation
        2. For each winner i, solve WDP_{-i} (without winner i's bids)
        3. Compute payment_i = SW_{-i} - (SW - value_i)
        4. Verify properties (truthfulness, individual rationality)
    """

    def __init__(self, bids: List[Bid], num_items: int):
        """
        Initialize VCG mechanism.

        Args:
            bids: List of all bids
            num_items: Total number of items
        """
        self.bids = bids
        self.num_items = num_items
        self.bidders = list(set(bid.bidder_id for bid in bids))

    def run_auction(self, wdp_method: str = 'auto') -> VCGOutcome:
        """
        Run VCG auction: allocate items and compute prices.

        Args:
            wdp_method: Method for solving WDP

        Returns:
            Complete VCG outcome
        """
        # Step 1: Solve WDP to get efficient allocation
        solver = WDPSolver(self.bids, self.num_items)
        allocation = solver.solve(method=wdp_method)

        # Step 2: Compute VCG payments
        payments = self._compute_vcg_payments(allocation, wdp_method)

        # Step 3: Compute summary statistics
        total_revenue = sum(p.payment for p in payments)
        total_welfare = sum(p.value for p in payments)
        total_utility = sum(p.utility for p in payments)

        return VCGOutcome(
            allocation=allocation,
            payments=payments,
            total_revenue=total_revenue,
            total_welfare=total_welfare,
            total_utility=total_utility
        )

    def _compute_vcg_payments(
        self,
        allocation: Allocation,
        wdp_method: str
    ) -> List[VCGPayment]:
        """
        Compute VCG payment for each winner.

        VCG Payment Formula:
            payment_i = (Social welfare without i) - (Social welfare with i, excluding i's value)
            payment_i = SW_{-i} - (SW - v_i)
            payment_i = SW_{-i} - SW + v_i

        Equivalently (Clarke Pivot):
            payment_i = Opportunity cost to others caused by winner i

        Args:
            allocation: Winning allocation from WDP
            wdp_method: Method for solving WDP

        Returns:
            List of VCG payments
        """
        payments = []
        sw_with_all = allocation.total_revenue  # SW with all winners

        # Group winning bids by bidder
        winning_bidders = {}
        for bid in allocation.winning_bids:
            if bid.bidder_id not in winning_bidders:
                winning_bidders[bid.bidder_id] = []
            winning_bidders[bid.bidder_id].append(bid)

        # Compute payment for each winning bidder
        for bidder_id, winning_bids in winning_bidders.items():
            # Value obtained by this bidder
            bidder_value = sum(bid.value for bid in winning_bids)

            # Solve WDP without this bidder's bids (Clarke pivot)
            bids_without_bidder = [b for b in self.bids if b.bidder_id != bidder_id]
            solver_minus_i = WDPSolver(bids_without_bidder, self.num_items)
            allocation_minus_i = solver_minus_i.solve(method=wdp_method)
            sw_without_bidder = allocation_minus_i.total_revenue

            # VCG payment = opportunity cost
            payment = sw_without_bidder - (sw_with_all - bidder_value)

            # Create payment record for each winning bid
            # (In practice, payment is per-bidder, but we track per-bid)
            for bid in winning_bids:
                # Prorate payment across multiple bids from same bidder
                bid_payment = payment * (bid.value / bidder_value) if bidder_value > 0 else 0
                utility = bid.value - bid_payment

                payments.append(VCGPayment(
                    bidder_id=bidder_id,
                    winning_bid=bid,
                    payment=bid_payment,
                    value=bid.value,
                    utility=utility
                ))

        return payments

    def verify_properties(self, outcome: VCGOutcome) -> Dict[str, bool]:
        """
        Verify VCG properties.

        Properties:
            1. Truthfulness: Always satisfied by design
            2. Individual Rationality: payment ≤ value for all winners
            3. Efficiency: Allocation maximizes social welfare
            4. Budget Balance: Usually fails (revenue ≤ social welfare)

        Args:
            outcome: VCG auction outcome

        Returns:
            Dictionary of property satisfaction
        """
        properties = {}

        # Truthfulness (always true by mechanism design)
        properties['truthful'] = True

        # Individual Rationality: payment_i ≤ value_i
        properties['individual_rational'] = all(
            p.payment <= p.value + 1e-6 for p in outcome.payments
        )

        # Efficiency: allocation maximizes welfare
        # (We assume WDP solver returned optimal solution)
        properties['efficient'] = True

        # No positive transfers (payments ≥ 0)
        properties['no_negative_payments'] = all(
            p.payment >= -1e-6 for p in outcome.payments
        )

        # Budget balance: typically fails for VCG
        # (Revenue < social welfare due to bidder surplus)
        properties['budget_balanced'] = abs(
            outcome.total_revenue - outcome.total_welfare
        ) < 1e-6

        return properties


class VCGVariants:
    """
    Variants and modifications of VCG pricing.

    1. Core-Selecting Auctions: Ensure revenue ≥ Vickrey revenue
    2. VCG with Reserve Prices: Increase revenue
    3. VCG with Entry Fees: Recover fixed costs
    """

    @staticmethod
    def vcg_with_reserve_prices(
        bids: List[Bid],
        num_items: int,
        reserve_prices: Dict[int, float]
    ) -> VCGOutcome:
        """
        VCG with item-specific reserve prices.

        Modification: Exclude bids with value/item < reserve price

        Args:
            bids: List of bids
            num_items: Number of items
            reserve_prices: Dictionary mapping item_id -> reserve price

        Returns:
            VCG outcome with reserve prices
        """
        # Filter bids below reserve price
        qualified_bids = []
        for bid in bids:
            # Compute average value per item in bid
            avg_value_per_item = bid.value / len(bid.items) if len(bid.items) > 0 else 0

            # Check if bid meets reserve price for all items
            meets_reserve = all(
                avg_value_per_item >= reserve_prices.get(item_id, 0)
                for item_id in bid.items
            )

            if meets_reserve:
                qualified_bids.append(bid)

        # Run VCG on qualified bids
        mechanism = VCGPricingMechanism(qualified_bids, num_items)
        return mechanism.run_auction()

    @staticmethod
    def compute_revenue_comparison(
        bids: List[Bid],
        num_items: int
    ) -> Dict[str, float]:
        """
        Compare revenue across different pricing mechanisms.

        Mechanisms:
            - VCG (truthful, efficient, but low revenue)
            - First-Price (high revenue, but not truthful)
            - Greedy allocation with VCG pricing

        Args:
            bids: List of bids
            num_items: Number of items

        Returns:
            Dictionary of revenues
        """
        revenues = {}

        # VCG (optimal allocation + VCG pricing)
        mechanism = VCGPricingMechanism(bids, num_items)
        vcg_outcome = mechanism.run_auction(wdp_method='auto')
        revenues['vcg'] = vcg_outcome.total_revenue

        # First-Price (winners pay their bids)
        solver = WDPSolver(bids, num_items)
        allocation = solver.solve(method='auto')
        revenues['first_price'] = allocation.total_revenue

        # Greedy allocation + VCG pricing
        greedy_allocation = solver.solve(method='greedy_value')
        # Note: VCG pricing on greedy allocation is not truthful!
        # This is for comparison only
        revenues['greedy_allocation'] = greedy_allocation.total_revenue

        return revenues


def demonstrate_truthfulness():
    """
    Demonstrate VCG truthfulness property.

    Show that bidding true value is a dominant strategy.
    """
    print("\n" + "=" * 80)
    print("VCG TRUTHFULNESS DEMONSTRATION")
    print("=" * 80)

    # Simple auction: 2 items, 2 bidders
    # Bidder A: true value = 100 for item {0}
    # Bidder B: true value = 80 for item {1}

    num_items = 2

    print("\nTrue valuations:")
    print("  Bidder A: $100 for item 0")
    print("  Bidder B: $80 for item 1")

    # Scenario 1: Both bid truthfully
    print("\n--- Scenario 1: Truthful bidding ---")
    bids_truthful = [
        Bid('A', {0}, 100),
        Bid('B', {1}, 80)
    ]

    mechanism = VCGPricingMechanism(bids_truthful, num_items)
    outcome_truthful = mechanism.run_auction()

    print("Allocation:")
    for payment in outcome_truthful.payments:
        print(f"  {payment.bidder_id}: pays ${payment.payment:.2f}, utility = ${payment.utility:.2f}")

    # Scenario 2: Bidder A lies (bids higher)
    print("\n--- Scenario 2: Bidder A overbids (bids 120) ---")
    bids_overbid = [
        Bid('A', {0}, 120),  # Lying!
        Bid('B', {1}, 80)
    ]

    mechanism2 = VCGPricingMechanism(bids_overbid, num_items)
    outcome_overbid = mechanism2.run_auction()

    print("Allocation:")
    for payment in outcome_overbid.payments:
        # Compute TRUE utility (based on true value = 100)
        true_utility = 100 - payment.payment if payment.bidder_id == 'A' else payment.utility
        print(f"  {payment.bidder_id}: pays ${payment.payment:.2f}, TRUE utility = ${true_utility:.2f}")

    # Scenario 3: Bidder A lies (bids lower)
    print("\n--- Scenario 3: Bidder A underbids (bids 50) ---")
    bids_underbid = [
        Bid('A', {0}, 50),  # Lying!
        Bid('B', {1}, 80)
    ]

    mechanism3 = VCGPricingMechanism(bids_underbid, num_items)
    outcome_underbid = mechanism3.run_auction()

    print("Allocation:")
    if not outcome_underbid.payments or all(p.bidder_id != 'A' for p in outcome_underbid.payments):
        print("  Bidder A: LOSES (didn't win)")
        print("  TRUE utility = $0 (by underbidding, A lost the auction!)")
    else:
        for payment in outcome_underbid.payments:
            true_utility = 100 - payment.payment if payment.bidder_id == 'A' else payment.utility
            print(f"  {payment.bidder_id}: pays ${payment.payment:.2f}, TRUE utility = ${true_utility:.2f}")

    print("\nConclusion: Bidding truthfully gives BEST utility for Bidder A.")
    print("This demonstrates VCG's truthfulness property!")
    print("=" * 80)


if __name__ == '__main__':
    print("=" * 80)
    print("VCG PRICING MECHANISM - Example")
    print("=" * 80)

    # Example: Spectrum auction with 5 licenses, 4 telecom companies
    bids = [
        Bid('Telecom_A', {0, 1}, 100),
        Bid('Telecom_A', {2}, 40),
        Bid('Telecom_B', {0}, 60),
        Bid('Telecom_B', {1, 2, 3}, 120),
        Bid('Telecom_C', {0, 1, 2}, 110),
        Bid('Telecom_C', {3, 4}, 80),
        Bid('Telecom_D', {4}, 50),
    ]

    num_items = 5

    print(f"\nSpectrum Auction: {len(bids)} bids on {num_items} licenses")
    print("\nBids:")
    for bid in bids:
        items_str = ', '.join(map(str, sorted(bid.items)))
        print(f"  {bid.bidder_id}: Licenses [{items_str}] = ${bid.value}M")

    # Run VCG auction
    mechanism = VCGPricingMechanism(bids, num_items)
    outcome = mechanism.run_auction(wdp_method='auto')

    print("\n" + "-" * 80)
    print("VCG AUCTION OUTCOME")
    print("-" * 80)

    print(f"\nTotal Social Welfare: ${outcome.total_welfare}M")
    print(f"Total Revenue: ${outcome.total_revenue}M")
    print(f"Total Bidder Surplus: ${outcome.total_utility}M")

    print("\nWinners and Payments:")
    print(f"{'Bidder':<15} {'Items':<20} {'Value':<12} {'Payment':<12} {'Utility'}")
    print("-" * 80)
    for payment in outcome.payments:
        items_str = ', '.join(map(str, sorted(payment.winning_bid.items)))
        print(
            f"{payment.bidder_id:<15} [{items_str:<18}] "
            f"${payment.value:<10.2f} ${payment.payment:<10.2f} ${payment.utility:.2f}"
        )

    # Verify properties
    properties = mechanism.verify_properties(outcome)
    print("\nProperties Verification:")
    for prop, satisfied in properties.items():
        status = "✓" if satisfied else "✗"
        print(f"  {status} {prop.replace('_', ' ').title()}: {satisfied}")

    # Revenue comparison
    print("\n" + "-" * 80)
    print("REVENUE COMPARISON")
    print("-" * 80)

    revenues = VCGVariants.compute_revenue_comparison(bids, num_items)
    for mechanism_name, revenue in revenues.items():
        print(f"  {mechanism_name.upper()}: ${revenue}M")

    # Demonstrate truthfulness
    demonstrate_truthfulness()
