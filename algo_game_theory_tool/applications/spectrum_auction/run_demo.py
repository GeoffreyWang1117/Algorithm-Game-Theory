"""
Spectrum Auction System Demo

Comprehensive demonstration of combinatorial spectrum auctions including:
1. Winner Determination Problem (WDP) algorithms
2. VCG pricing mechanism
3. Real-world FCC auction scenarios
4. Algorithm performance comparison
5. Revenue analysis

Demonstrates:
- Multiple WDP solving algorithms (greedy, branch-and-bound, exhaustive)
- VCG truthful pricing
- FCC Auction 73 inspired scenario
- Visualization and analysis
"""

import sys
import os
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Set
import time

sys.path.append(str(Path(__file__).parent))

from wdp_solver import Bid, WDPSolver, Allocation, compare_algorithms
from vcg_pricing import VCGPricingMechanism, VCGOutcome, VCGVariants


class BidGenerator:
    """Generate realistic bids for spectrum auctions."""

    def __init__(self, num_items: int, num_bidders: int, seed: int = 42):
        """
        Initialize bid generator.

        Args:
            num_items: Number of spectrum licenses
            num_items: Number of bidders (telecom companies)
            seed: Random seed
        """
        self.num_items = num_items
        self.num_bidders = num_bidders
        self.rng = np.random.RandomState(seed)
        self.bidder_ids = [f'Bidder_{i:02d}' for i in range(num_bidders)]

    def generate_bids(
        self,
        bids_per_bidder: int = 3,
        max_bundle_size: int = None,
        value_range: Tuple[float, float] = (10, 200)
    ) -> List[Bid]:
        """
        Generate synthetic bids.

        Bidding strategy:
            - Each bidder submits multiple bids on different bundles
            - Bundle values exhibit complementarities (superadditive)
            - Larger bundles have higher total value (economies of scale)

        Args:
            bids_per_bidder: Number of bids per bidder
            max_bundle_size: Maximum items in a bundle
            value_range: (min, max) value range

        Returns:
            List of generated bids
        """
        if max_bundle_size is None:
            max_bundle_size = min(self.num_items, 5)

        bids = []

        for bidder_id in self.bidder_ids:
            # Each bidder has preferences over certain licenses
            # E.g., geographic regions, spectrum bands

            for _ in range(bids_per_bidder):
                # Random bundle size (prefer smaller bundles)
                bundle_size = self.rng.choice(
                    range(1, max_bundle_size + 1),
                    p=self._bundle_size_distribution(max_bundle_size)
                )

                # Select random items
                items = set(self.rng.choice(
                    self.num_items,
                    size=bundle_size,
                    replace=False
                ))

                # Generate value with complementarities
                # Base value: sum of individual values
                # Synergy bonus: extra value for bundles
                base_value_per_item = self.rng.uniform(*value_range)
                total_base_value = base_value_per_item * bundle_size

                # Synergy: larger bundles have higher value per item
                synergy_factor = 1.0 + 0.2 * (bundle_size - 1)
                value = total_base_value * synergy_factor

                bids.append(Bid(bidder_id, items, value))

        return bids

    def _bundle_size_distribution(self, max_size: int) -> np.ndarray:
        """Probability distribution favoring smaller bundles."""
        # Geometric-like distribution
        probs = np.array([1.0 / (2 ** i) for i in range(max_size)])
        return probs / probs.sum()

    def generate_fcc_style_bids(self) -> List[Bid]:
        """
        Generate bids inspired by FCC Auction 73 (700 MHz, 2008).

        Scenario:
            - Regional and national licenses
            - Large carriers want national coverage
            - Regional carriers want specific areas
            - Mix of single-license and bundle bids

        Returns:
            List of realistic bids
        """
        bids = []

        # Assume items 0-9 are regional licenses, 10+ are national
        regional_licenses = list(range(min(10, self.num_items)))
        national_licenses = list(range(10, self.num_items)) if self.num_items > 10 else []

        # Large national carriers (first 2 bidders)
        for i in range(min(2, self.num_bidders)):
            bidder_id = self.bidder_ids[i]

            # Bid on national coverage (all or most licenses)
            if self.num_items >= 5:
                all_licenses = set(range(self.num_items))
                # High value for national coverage
                value = self.rng.uniform(300, 500)
                bids.append(Bid(bidder_id, all_licenses, value))

            # Bid on regional bundles as fallback
            for _ in range(2):
                bundle_size = self.rng.randint(3, min(7, self.num_items))
                items = set(self.rng.choice(self.num_items, bundle_size, replace=False))
                value = self.rng.uniform(100, 200)
                bids.append(Bid(bidder_id, items, value))

        # Regional carriers (remaining bidders)
        for i in range(2, self.num_bidders):
            bidder_id = self.bidder_ids[i]

            # Bid on specific regional licenses
            for _ in range(3):
                bundle_size = self.rng.randint(1, 4)
                items = set(self.rng.choice(
                    min(10, self.num_items),
                    bundle_size,
                    replace=False
                ))
                value = self.rng.uniform(20, 100)
                bids.append(Bid(bidder_id, items, value))

        return bids


class SpectrumAuctionDemo:
    """Comprehensive spectrum auction demonstration."""

    def __init__(self, output_dir: str = 'visualization'):
        """Initialize demo."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (14, 10)

    def demo_wdp_algorithms(self):
        """Demonstrate WDP solving algorithms."""
        print("\n" + "=" * 100)
        print("DEMO 1: WINNER DETERMINATION PROBLEM (WDP) ALGORITHMS")
        print("=" * 100)

        # Generate test scenario
        num_items = 10
        num_bidders = 6

        generator = BidGenerator(num_items, num_bidders, seed=42)
        bids = generator.generate_bids(bids_per_bidder=3, max_bundle_size=4)

        print(f"\nScenario: {len(bids)} bids on {num_items} spectrum licenses")
        print(f"Bidders: {num_bidders} telecom companies")

        print(f"\nSample bids:")
        for bid in bids[:10]:
            items_str = ','.join(map(str, sorted(bid.items)))
            print(f"  {bid.bidder_id}: [{items_str}] = ${bid.value:.1f}M")
        if len(bids) > 10:
            print(f"  ... and {len(bids) - 10} more bids")

        # Compare algorithms
        print("\n" + "-" * 100)
        print("Algorithm Comparison")
        print("-" * 100)

        results = compare_algorithms(bids, num_items)

        print(f"\n{'Algorithm':<20} {'Revenue ($M)':<15} {'Time (ms)':<12} {'Efficiency':<12} {'# Winners'}")
        print("-" * 100)

        for method, allocation in sorted(results.items()):
            print(
                f"{method:<20} ${allocation.total_revenue:<13.1f} "
                f"{allocation.computation_time*1000:<11.2f} "
                f"{allocation.efficiency(num_items)*100:<11.1f}% "
                f"{len(allocation.winning_bids)}"
            )

        # Visualize
        self._visualize_wdp_comparison(results, num_items)

        return bids, num_items

    def demo_vcg_pricing(self, bids: List[Bid], num_items: int):
        """Demonstrate VCG pricing mechanism."""
        print("\n" + "=" * 100)
        print("DEMO 2: VCG PRICING MECHANISM")
        print("=" * 100)

        # Run VCG auction
        mechanism = VCGPricingMechanism(bids, num_items)
        outcome = mechanism.run_auction(wdp_method='auto')

        print(f"\nAuction Results:")
        print(f"  Total Social Welfare: ${outcome.total_welfare:.1f}M")
        print(f"  Total Revenue (VCG): ${outcome.total_revenue:.1f}M")
        print(f"  Total Bidder Surplus: ${outcome.total_utility:.1f}M")
        print(f"  Number of Winners: {len(set(p.bidder_id for p in outcome.payments))}")

        print(f"\nWinning Bids:")
        print(f"{'Bidder':<15} {'Licenses':<25} {'Value ($M)':<12} {'Payment ($M)':<15} {'Utility ($M)'}")
        print("-" * 100)

        # Group by bidder
        bidder_summary = {}
        for payment in outcome.payments:
            if payment.bidder_id not in bidder_summary:
                bidder_summary[payment.bidder_id] = {
                    'items': set(),
                    'value': 0,
                    'payment': 0,
                    'utility': 0
                }
            bidder_summary[payment.bidder_id]['items'] |= payment.winning_bid.items
            bidder_summary[payment.bidder_id]['value'] += payment.value
            bidder_summary[payment.bidder_id]['payment'] += payment.payment
            bidder_summary[payment.bidder_id]['utility'] += payment.utility

        for bidder_id, summary in sorted(bidder_summary.items()):
            items_str = ','.join(map(str, sorted(summary['items'])))
            print(
                f"{bidder_id:<15} [{items_str:<23}] "
                f"${summary['value']:<10.1f} ${summary['payment']:<13.1f} ${summary['utility']:.1f}"
            )

        # Verify properties
        properties = mechanism.verify_properties(outcome)
        print("\nVCG Properties:")
        for prop, satisfied in properties.items():
            status = "✓" if satisfied else "✗"
            print(f"  {status} {prop.replace('_', ' ').title()}")

        # Visualize
        self._visualize_vcg_outcome(outcome)

        return outcome

    def demo_fcc_auction_73(self):
        """Simulate FCC Auction 73 style scenario."""
        print("\n" + "=" * 100)
        print("DEMO 3: FCC AUCTION 73 STYLE SCENARIO (700 MHz Spectrum)")
        print("=" * 100)

        print("\nBackground:")
        print("  FCC Auction 73 (2008): Auctioned 700 MHz spectrum (analog TV transition)")
        print("  Result: $19.6 billion, 1,090 licenses across US")
        print("  Winners: Verizon ($9.4B), AT&T ($6.6B), regional carriers")

        # Generate FCC-style bids
        num_items = 12  # Represent 12 major regions
        num_bidders = 8  # Mix of national and regional carriers

        generator = BidGenerator(num_items, num_bidders, seed=73)
        bids = generator.generate_fcc_style_bids()

        print(f"\nSimulation: {len(bids)} bids on {num_items} regional spectrum blocks")
        print(f"Bidders: {num_bidders} carriers (2 national, 6 regional)")

        # Run auction with VCG
        mechanism = VCGPricingMechanism(bids, num_items)
        outcome = mechanism.run_auction(wdp_method='branch_and_bound')

        print(f"\n" + "-" * 100)
        print("Auction Outcome")
        print("-" * 100)

        print(f"\nTotal Revenue: ${outcome.total_revenue:.1f}M")
        print(f"Social Welfare: ${outcome.total_welfare:.1f}M")

        # Winner summary
        winner_summary = {}
        for payment in outcome.payments:
            if payment.bidder_id not in winner_summary:
                winner_summary[payment.bidder_id] = {
                    'licenses': set(),
                    'payment': 0
                }
            winner_summary[payment.bidder_id]['licenses'] |= payment.winning_bid.items
            winner_summary[payment.bidder_id]['payment'] += payment.payment

        print(f"\nWinners by Market Share:")
        sorted_winners = sorted(
            winner_summary.items(),
            key=lambda x: x[1]['payment'],
            reverse=True
        )

        for rank, (bidder_id, data) in enumerate(sorted_winners, 1):
            num_licenses = len(data['licenses'])
            market_share = num_licenses / num_items * 100
            revenue_share = data['payment'] / outcome.total_revenue * 100
            print(
                f"  {rank}. {bidder_id}: {num_licenses} licenses ({market_share:.1f}%), "
                f"${data['payment']:.1f}M ({revenue_share:.1f}% of revenue)"
            )

        return outcome

    def demo_revenue_comparison(self):
        """Compare revenue across different mechanisms."""
        print("\n" + "=" * 100)
        print("DEMO 4: REVENUE COMPARISON ACROSS MECHANISMS")
        print("=" * 100)

        num_items = 10
        num_bidders = 6

        generator = BidGenerator(num_items, num_bidders, seed=123)
        bids = generator.generate_bids(bids_per_bidder=4)

        print(f"\nScenario: {len(bids)} bids, {num_items} items")

        # Compare mechanisms
        revenues = VCGVariants.compute_revenue_comparison(bids, num_items)

        print(f"\nRevenue Comparison:")
        print(f"{'Mechanism':<25} {'Revenue ($M)':<15} {'vs VCG'}")
        print("-" * 70)

        vcg_revenue = revenues['vcg']
        for mechanism, revenue in sorted(revenues.items(), key=lambda x: x[1], reverse=True):
            diff_pct = (revenue - vcg_revenue) / vcg_revenue * 100 if vcg_revenue > 0 else 0
            print(f"{mechanism.upper():<25} ${revenue:<13.1f} {diff_pct:+.1f}%")

        print("\nKey Insights:")
        print("  • First-Price maximizes revenue but is NOT truthful")
        print("  • VCG ensures truthfulness but may yield lower revenue")
        print("  • Trade-off: Efficiency vs Revenue")

        # Visualize
        self._visualize_revenue_comparison(revenues)

    def _visualize_wdp_comparison(self, results: Dict[str, Allocation], num_items: int):
        """Visualize WDP algorithm comparison."""
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))

        methods = list(results.keys())
        revenues = [results[m].total_revenue for m in methods]
        times = [results[m].computation_time * 1000 for m in methods]  # ms
        efficiencies = [results[m].efficiency(num_items) * 100 for m in methods]

        # Plot 1: Revenue
        axes[0].bar(range(len(methods)), revenues, color='steelblue', alpha=0.7)
        axes[0].set_xlabel('Algorithm')
        axes[0].set_ylabel('Revenue ($M)')
        axes[0].set_title('Revenue Comparison')
        axes[0].set_xticks(range(len(methods)))
        axes[0].set_xticklabels(methods, rotation=45, ha='right')
        axes[0].grid(axis='y', alpha=0.3)

        # Plot 2: Computation Time
        axes[1].bar(range(len(methods)), times, color='coral', alpha=0.7)
        axes[1].set_xlabel('Algorithm')
        axes[1].set_ylabel('Time (ms)')
        axes[1].set_title('Computation Time')
        axes[1].set_xticks(range(len(methods)))
        axes[1].set_xticklabels(methods, rotation=45, ha='right')
        axes[1].set_yscale('log')
        axes[1].grid(axis='y', alpha=0.3)

        # Plot 3: Efficiency
        axes[2].bar(range(len(methods)), efficiencies, color='mediumseagreen', alpha=0.7)
        axes[2].set_xlabel('Algorithm')
        axes[2].set_ylabel('Efficiency (%)')
        axes[2].set_title('Allocation Efficiency')
        axes[2].set_xticks(range(len(methods)))
        axes[2].set_xticklabels(methods, rotation=45, ha='right')
        axes[2].set_ylim([0, 105])
        axes[2].grid(axis='y', alpha=0.3)

        plt.tight_layout()
        save_path = self.output_dir / 'wdp_comparison.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\nVisualization saved to {save_path}")

    def _visualize_vcg_outcome(self, outcome: VCGOutcome):
        """Visualize VCG auction outcome."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Group by bidder
        bidder_data = {}
        for payment in outcome.payments:
            if payment.bidder_id not in bidder_data:
                bidder_data[payment.bidder_id] = {'value': 0, 'payment': 0, 'utility': 0}
            bidder_data[payment.bidder_id]['value'] += payment.value
            bidder_data[payment.bidder_id]['payment'] += payment.payment
            bidder_data[payment.bidder_id]['utility'] += payment.utility

        bidders = list(bidder_data.keys())
        values = [bidder_data[b]['value'] for b in bidders]
        payments = [bidder_data[b]['payment'] for b in bidders]
        utilities = [bidder_data[b]['utility'] for b in bidders]

        # Plot 1: Value vs Payment
        x = np.arange(len(bidders))
        width = 0.35

        axes[0].bar(x - width/2, values, width, label='Declared Value', alpha=0.8)
        axes[0].bar(x + width/2, payments, width, label='VCG Payment', alpha=0.8)
        axes[0].set_xlabel('Winning Bidder')
        axes[0].set_ylabel('Amount ($M)')
        axes[0].set_title('Value vs Payment')
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(bidders, rotation=45, ha='right')
        axes[0].legend()
        axes[0].grid(axis='y', alpha=0.3)

        # Plot 2: Utility Distribution
        axes[1].bar(x, utilities, color='green', alpha=0.7)
        axes[1].set_xlabel('Winning Bidder')
        axes[1].set_ylabel('Utility ($M)')
        axes[1].set_title('Bidder Surplus (Utility)')
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(bidders, rotation=45, ha='right')
        axes[1].grid(axis='y', alpha=0.3)

        plt.tight_layout()
        save_path = self.output_dir / 'vcg_outcome.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Visualization saved to {save_path}")

    def _visualize_revenue_comparison(self, revenues: Dict[str, float]):
        """Visualize revenue comparison across mechanisms."""
        fig, ax = plt.subplots(figsize=(10, 6))

        mechanisms = list(revenues.keys())
        amounts = [revenues[m] for m in mechanisms]

        colors = ['steelblue' if m == 'vcg' else 'coral' for m in mechanisms]

        ax.bar(range(len(mechanisms)), amounts, color=colors, alpha=0.7)
        ax.set_xlabel('Mechanism')
        ax.set_ylabel('Revenue ($M)')
        ax.set_title('Revenue Comparison Across Auction Mechanisms')
        ax.set_xticks(range(len(mechanisms)))
        ax.set_xticklabels([m.upper() for m in mechanisms], rotation=0)
        ax.grid(axis='y', alpha=0.3)

        # Add value labels
        for i, v in enumerate(amounts):
            ax.text(i, v + max(amounts)*0.02, f'${v:.1f}M', ha='center', va='bottom')

        plt.tight_layout()
        save_path = self.output_dir / 'revenue_comparison.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Visualization saved to {save_path}")

    def run_all_demos(self):
        """Run all demonstration scenarios."""
        print("\n" + "=" * 100)
        print(" " * 25 + "SPECTRUM AUCTION SYSTEM - COMPREHENSIVE DEMO")
        print("=" * 100)
        print("\nDemonstrating combinatorial spectrum auctions with:")
        print("  1. Winner Determination Problem (WDP) algorithms")
        print("  2. VCG (Vickrey-Clarke-Groves) pricing")
        print("  3. FCC Auction 73 style scenario")
        print("  4. Revenue comparison across mechanisms")

        # Run demos
        bids, num_items = self.demo_wdp_algorithms()
        self.demo_vcg_pricing(bids, num_items)
        self.demo_fcc_auction_73()
        self.demo_revenue_comparison()

        print("\n" + "=" * 100)
        print("ALL DEMOS COMPLETED")
        print("=" * 100)
        print(f"\nVisualizations saved to: {self.output_dir.absolute()}")
        print("\nKey Takeaways:")
        print("  • WDP is NP-hard: Greedy is fast, exact algorithms slow for large instances")
        print("  • VCG ensures truthfulness and efficiency")
        print("  • VCG typically yields lower revenue than first-price auctions")
        print("  • Real FCC auctions use sophisticated variants (SMR, clock auctions)")
        print("  • Trade-off: Simplicity vs Revenue vs Truthfulness")
        print("\n" + "=" * 100)


if __name__ == '__main__':
    # Run comprehensive demonstration
    demo = SpectrumAuctionDemo(output_dir='visualization')
    demo.run_all_demos()
