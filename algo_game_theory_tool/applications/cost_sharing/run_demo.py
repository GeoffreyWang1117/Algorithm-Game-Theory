"""
Cost Sharing System Demo

This script demonstrates all cost sharing applications:
1. Cloud computing resource cost allocation
2. Rideshare cost distribution
3. Comparative analysis of Shapley value vs. other methods

Runs end-to-end simulations with visualization and analysis.
"""

import sys
import os
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List
import yaml
import time

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from shapley_value import ShapleyValue, ShapleyAnalyzer, compare_algorithms
from cloud_cost_sharing import (
    CloudCostSharingSystem,
    create_example_scenario as create_cloud_scenario
)
from rideshare_cost import (
    RideshareCostSharingSystem,
    create_example_scenario as create_rideshare_scenario
)


class CostSharingDemo:
    """
    Comprehensive demonstration of cost sharing mechanisms.
    """

    def __init__(self, output_dir: str = 'visualization'):
        """
        Initialize demo.

        Args:
            output_dir: Directory for output visualizations
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

        # Set plotting style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10

    def demo_cloud_cost_sharing(self):
        """Demonstrate cloud computing cost sharing."""
        print("\n" + "=" * 100)
        print("DEMO 1: CLOUD COMPUTING COST SHARING")
        print("=" * 100)

        # Create scenario
        system = create_cloud_scenario()

        print("\nScenario: 5 departments sharing corporate AWS infrastructure")
        print("\nCustomer Details:")
        print("-" * 100)
        print(f"{'Department':<25} {'CPU Cores':<12} {'Memory (GB)':<15} {'Storage (GB)':<15} {'Network (Gbps)'}")
        print("-" * 100)

        for customer in system.customers:
            print(
                f"{customer.name:<25} {customer.cpu_cores:>10.0f} "
                f"{customer.memory_gb:>13.0f} {customer.storage_gb:>13.0f} "
                f"{customer.network_gbps:>14.1f}"
            )

        # Compute allocations
        print("\n" + "-" * 100)
        print("Computing Shapley value allocation...")
        print("-" * 100)

        start_time = time.time()
        allocation = system.allocate_costs(method='exact')
        computation_time = time.time() - start_time

        print(f"\nComputation time: {computation_time:.3f} seconds")
        print(system.get_allocation_summary(allocation))

        # Visualize
        self._visualize_cloud_allocation(system, allocation)

        return allocation

    def demo_rideshare_cost_sharing(self):
        """Demonstrate rideshare cost sharing."""
        print("\n" + "=" * 100)
        print("DEMO 2: RIDESHARE COST ALLOCATION")
        print("=" * 100)

        # Create scenario
        system = create_rideshare_scenario()

        print("\nScenario: 4 coworkers sharing morning commute")
        print("Pricing: $5 base + $1.50/mile, no surge")

        print("\nRider Details:")
        print("-" * 100)
        print(f"{'Name':<15} {'Pickup':<25} {'Dropoff':<25} {'Solo Distance':<15} {'Solo Cost'}")
        print("-" * 100)

        for rider in system.riders:
            solo_distance = system.origin.distance_to(rider.pickup) + \
                           rider.pickup.distance_to(rider.dropoff)
            solo_cost = system.cost_function({rider.id})
            print(
                f"{rider.name:<15} {rider.pickup.name:<25} {rider.dropoff.name:<25} "
                f"{solo_distance:>13.2f} mi ${solo_cost:>9.2f}"
            )

        # Compute allocation
        print("\n" + "-" * 100)
        print("Computing Shapley value allocation...")
        print("-" * 100)

        start_time = time.time()
        allocation = system.allocate_costs(method='exact')
        computation_time = time.time() - start_time

        print(f"\nComputation time: {computation_time:.3f} seconds")
        print(system.get_allocation_summary(allocation))

        # Visualize
        fig = system.visualize_allocation(
            allocation,
            save_path=str(self.output_dir / 'rideshare_allocation.png')
        )

        return allocation

    def demo_algorithm_comparison(self):
        """Compare different Shapley value computation algorithms."""
        print("\n" + "=" * 100)
        print("DEMO 3: ALGORITHM COMPARISON")
        print("=" * 100)

        # Use cloud scenario for comparison
        system = create_cloud_scenario()
        players = [c.id for c in system.customers]

        print(f"\nComparing algorithms on {len(players)}-player game...")
        print("Algorithms: Exact, Monte Carlo (1000 samples), Incremental")

        # Time each algorithm
        results = {}
        times = {}

        # Exact
        print("\n1. Exact algorithm:")
        start = time.time()
        results['exact'] = system.shapley_calculator.exact()
        times['exact'] = time.time() - start
        print(f"   Time: {times['exact']:.3f} seconds")

        # Monte Carlo
        print("\n2. Monte Carlo (1000 samples):")
        start = time.time()
        results['monte_carlo_1k'] = system.shapley_calculator.monte_carlo(num_samples=1000, seed=42)
        times['monte_carlo_1k'] = time.time() - start
        print(f"   Time: {times['monte_carlo_1k']:.3f} seconds")

        # Monte Carlo with more samples
        print("\n3. Monte Carlo (10000 samples):")
        start = time.time()
        results['monte_carlo_10k'] = system.shapley_calculator.monte_carlo(num_samples=10000, seed=42)
        times['monte_carlo_10k'] = time.time() - start
        print(f"   Time: {times['monte_carlo_10k']:.3f} seconds")

        # Compare accuracy
        print("\n" + "-" * 100)
        print("Accuracy Comparison (vs. Exact)")
        print("-" * 100)
        print(f"{'Player':<20} {'Exact':<15} {'MC 1k':<15} {'Error 1k':<12} {'MC 10k':<15} {'Error 10k'}")
        print("-" * 100)

        exact = results['exact']
        mc_1k = results['monte_carlo_1k']
        mc_10k = results['monte_carlo_10k']

        errors_1k = []
        errors_10k = []

        for player in players:
            e = exact[player]
            m1 = mc_1k[player]
            m2 = mc_10k[player]
            err1 = abs(e - m1)
            err2 = abs(e - m2)

            errors_1k.append(err1 / e * 100 if e > 0 else 0)
            errors_10k.append(err2 / e * 100 if e > 0 else 0)

            print(
                f"{player:<20} ${e:>12,.2f} ${m1:>12,.2f} "
                f"${err1:>9,.2f} ${m2:>12,.2f} ${err2:>9,.2f}"
            )

        print("\n" + "-" * 100)
        print(f"Average error (1k samples): {np.mean(errors_1k):.2f}%")
        print(f"Average error (10k samples): {np.mean(errors_10k):.2f}%")
        print(f"Max error (1k samples): {np.max(errors_1k):.2f}%")
        print(f"Max error (10k samples): {np.max(errors_10k):.2f}%")

        # Visualize comparison
        self._visualize_algorithm_comparison(players, results, times)

        return results, times

    def demo_fairness_comparison(self):
        """Compare Shapley allocation with other methods."""
        print("\n" + "=" * 100)
        print("DEMO 4: FAIRNESS COMPARISON")
        print("=" * 100)

        # Use cloud scenario
        system = create_cloud_scenario()

        print("\nComparing allocation methods:")
        print("1. Shapley Value (game-theoretic fair division)")
        print("2. Proportional (based on resource usage)")
        print("3. Equal Split (everyone pays same amount)")

        # Compute Shapley allocation
        shapley = system.allocate_costs(method='exact')

        # Compute proportional allocation
        total_cost = sum(shapley.values())

        # Proportional: based on resource consumption
        total_resources = 0
        customer_resources = {}

        for customer in system.customers:
            resources = (
                customer.cpu_cores * system.cost_model.cpu_price_per_core +
                customer.memory_gb * system.cost_model.memory_price_per_gb +
                customer.storage_gb * system.cost_model.storage_price_per_gb +
                customer.network_gbps * system.cost_model.network_price_per_gbps
            )
            customer_resources[customer.id] = resources
            total_resources += resources

        proportional = {
            cid: total_cost * (customer_resources[cid] / total_resources)
            for cid in shapley.keys()
        }

        # Equal split
        equal = {cid: total_cost / len(shapley) for cid in shapley.keys()}

        # Compare
        print("\n" + "-" * 100)
        print(f"{'Customer':<20} {'Shapley':<15} {'Proportional':<15} {'Equal Split':<15} {'Savings (Shapley)'}")
        print("-" * 100)

        for customer_id in sorted(shapley.keys()):
            s = shapley[customer_id]
            p = proportional[customer_id]
            e = equal[customer_id]

            standalone = system.cost_function({customer_id})
            savings = standalone - s
            savings_pct = (savings / standalone * 100) if standalone > 0 else 0

            print(
                f"{customer_id:<20} ${s:>12,.2f} ${p:>12,.2f} "
                f"${e:>12,.2f} ${savings:>10,.2f} ({savings_pct:>4.1f}%)"
            )

        # Analyze fairness properties
        print("\n" + "-" * 100)
        print("Fairness Properties")
        print("-" * 100)

        analyzer = system.analyzer

        for method_name, allocation in [('Shapley', shapley), ('Proportional', proportional), ('Equal', equal)]:
            print(f"\n{method_name}:")

            # Efficiency
            is_eff = analyzer.verify_efficiency(allocation)
            print(f"  ✓ Efficiency (budget balance): {is_eff}")

            # Individual rationality
            ir = analyzer.verify_individual_rationality(allocation)
            all_ir = all(ir.values())
            print(f"  {'✓' if all_ir else '✗'} Individual Rationality: {all_ir}")
            if not all_ir:
                violators = [k for k, v in ir.items() if not v]
                print(f"    Violators: {violators}")

            # Core membership
            is_core, blocking = analyzer.check_core_membership(allocation)
            print(f"  {'✓' if is_core else '✗'} Core Membership (stability): {is_core}")
            if not is_core:
                print(f"    Number of blocking coalitions: {len(blocking)}")

        # Visualize
        self._visualize_fairness_comparison(system.customers, shapley, proportional, equal)

        return shapley, proportional, equal

    def _visualize_cloud_allocation(self, system, allocation: Dict[str, float]):
        """Visualize cloud cost allocation."""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        customer_names = [system.customer_db[cid].name for cid in allocation.keys()]
        allocated_costs = [allocation[cid] for cid in allocation.keys()]
        standalone_costs = [system.cost_function({cid}) for cid in allocation.keys()]
        savings = [standalone_costs[i] - allocated_costs[i] for i in range(len(customer_names))]

        # Plot 1: Allocated vs Standalone
        x = np.arange(len(customer_names))
        width = 0.35

        axes[0, 0].bar(x - width/2, standalone_costs, width, label='Standalone', alpha=0.8, color='indianred')
        axes[0, 0].bar(x + width/2, allocated_costs, width, label='Shared (Shapley)', alpha=0.8, color='steelblue')
        axes[0, 0].set_xlabel('Customer')
        axes[0, 0].set_ylabel('Monthly Cost ($)')
        axes[0, 0].set_title('Cost Comparison: Standalone vs. Shared Infrastructure')
        axes[0, 0].set_xticks(x)
        axes[0, 0].set_xticklabels(customer_names, rotation=45, ha='right')
        axes[0, 0].legend()
        axes[0, 0].grid(axis='y', alpha=0.3)

        # Plot 2: Savings
        colors = ['green' if s > 0 else 'red' for s in savings]
        axes[0, 1].bar(x, savings, color=colors, alpha=0.7)
        axes[0, 1].axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        axes[0, 1].set_xlabel('Customer')
        axes[0, 1].set_ylabel('Savings ($)')
        axes[0, 1].set_title('Savings from Resource Sharing')
        axes[0, 1].set_xticks(x)
        axes[0, 1].set_xticklabels(customer_names, rotation=45, ha='right')
        axes[0, 1].grid(axis='y', alpha=0.3)

        # Plot 3: Cost breakdown by resource type
        resource_costs = []
        for cid in allocation.keys():
            customer = system.customer_db[cid]
            costs = {
                'CPU': customer.cpu_cores * system.cost_model.cpu_price_per_core,
                'Memory': customer.memory_gb * system.cost_model.memory_price_per_gb,
                'Storage': customer.storage_gb * system.cost_model.storage_price_per_gb,
                'Network': customer.network_gbps * system.cost_model.network_price_per_gbps
            }
            resource_costs.append(costs)

        resources = ['CPU', 'Memory', 'Storage', 'Network']
        bottom = np.zeros(len(customer_names))

        for resource in resources:
            values = [rc[resource] for rc in resource_costs]
            axes[1, 0].bar(x, values, width * 2, label=resource, bottom=bottom, alpha=0.8)
            bottom += values

        axes[1, 0].set_xlabel('Customer')
        axes[1, 0].set_ylabel('Resource Cost ($)')
        axes[1, 0].set_title('Resource Cost Breakdown (Pre-sharing)')
        axes[1, 0].set_xticks(x)
        axes[1, 0].set_xticklabels(customer_names, rotation=45, ha='right')
        axes[1, 0].legend()
        axes[1, 0].grid(axis='y', alpha=0.3)

        # Plot 4: Cost reduction percentage
        reduction_pct = [(savings[i] / standalone_costs[i] * 100) if standalone_costs[i] > 0 else 0
                        for i in range(len(customer_names))]

        axes[1, 1].bar(x, reduction_pct, color='mediumseagreen', alpha=0.7)
        axes[1, 1].set_xlabel('Customer')
        axes[1, 1].set_ylabel('Cost Reduction (%)')
        axes[1, 1].set_title('Cost Reduction Percentage')
        axes[1, 1].set_xticks(x)
        axes[1, 1].set_xticklabels(customer_names, rotation=45, ha='right')
        axes[1, 1].grid(axis='y', alpha=0.3)
        axes[1, 1].axhline(y=np.mean(reduction_pct), color='red', linestyle='--',
                          label=f'Average: {np.mean(reduction_pct):.1f}%')
        axes[1, 1].legend()

        plt.tight_layout()
        save_path = self.output_dir / 'cloud_cost_allocation.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\nVisualization saved to {save_path}")

        return fig

    def _visualize_algorithm_comparison(self, players: List[str],
                                       results: Dict, times: Dict):
        """Visualize algorithm comparison."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Plot 1: Accuracy comparison
        exact = results['exact']
        mc_1k = results['monte_carlo_1k']
        mc_10k = results['monte_carlo_10k']

        x = np.arange(len(players))
        width = 0.25

        exact_vals = [exact[p] for p in players]
        mc1k_vals = [mc_1k[p] for p in players]
        mc10k_vals = [mc_10k[p] for p in players]

        axes[0].bar(x - width, exact_vals, width, label='Exact', alpha=0.8)
        axes[0].bar(x, mc1k_vals, width, label='MC 1k', alpha=0.8)
        axes[0].bar(x + width, mc10k_vals, width, label='MC 10k', alpha=0.8)

        axes[0].set_xlabel('Player')
        axes[0].set_ylabel('Allocated Cost ($)')
        axes[0].set_title('Algorithm Accuracy Comparison')
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(players, rotation=45, ha='right')
        axes[0].legend()
        axes[0].grid(axis='y', alpha=0.3)

        # Plot 2: Computation time
        methods = list(times.keys())
        time_vals = list(times.values())

        axes[1].bar(methods, time_vals, color=['steelblue', 'coral', 'mediumseagreen'], alpha=0.7)
        axes[1].set_ylabel('Computation Time (seconds)')
        axes[1].set_title('Algorithm Performance')
        axes[1].set_xticks(range(len(methods)))
        axes[1].set_xticklabels(['Exact', 'MC 1k', 'MC 10k'], rotation=0)
        axes[1].grid(axis='y', alpha=0.3)

        # Add time labels on bars
        for i, v in enumerate(time_vals):
            axes[1].text(i, v + max(time_vals) * 0.02, f'{v:.3f}s',
                        ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        save_path = self.output_dir / 'algorithm_comparison.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\nVisualization saved to {save_path}")

        return fig

    def _visualize_fairness_comparison(self, customers, shapley, proportional, equal):
        """Visualize comparison of allocation methods."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        customer_names = [c.name for c in customers]
        shapley_vals = [shapley[c.id] for c in customers]
        prop_vals = [proportional[c.id] for c in customers]
        equal_vals = [equal[c.id] for c in customers]

        x = np.arange(len(customer_names))
        width = 0.25

        # Plot 1: Allocation comparison
        axes[0].bar(x - width, shapley_vals, width, label='Shapley', alpha=0.8, color='steelblue')
        axes[0].bar(x, prop_vals, width, label='Proportional', alpha=0.8, color='coral')
        axes[0].bar(x + width, equal_vals, width, label='Equal Split', alpha=0.8, color='mediumseagreen')

        axes[0].set_xlabel('Customer')
        axes[0].set_ylabel('Allocated Cost ($)')
        axes[0].set_title('Allocation Method Comparison')
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(customer_names, rotation=45, ha='right')
        axes[0].legend()
        axes[0].grid(axis='y', alpha=0.3)

        # Plot 2: Difference from Shapley
        prop_diff = [prop_vals[i] - shapley_vals[i] for i in range(len(customer_names))]
        equal_diff = [equal_vals[i] - shapley_vals[i] for i in range(len(customer_names))]

        axes[1].bar(x - width/2, prop_diff, width, label='Proportional - Shapley', alpha=0.8)
        axes[1].bar(x + width/2, equal_diff, width, label='Equal - Shapley', alpha=0.8)
        axes[1].axhline(y=0, color='black', linestyle='-', linewidth=0.8)

        axes[1].set_xlabel('Customer')
        axes[1].set_ylabel('Difference from Shapley ($)')
        axes[1].set_title('Deviation from Shapley Allocation')
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(customer_names, rotation=45, ha='right')
        axes[1].legend()
        axes[1].grid(axis='y', alpha=0.3)

        plt.tight_layout()
        save_path = self.output_dir / 'fairness_comparison.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\nVisualization saved to {save_path}")

        return fig

    def run_all_demos(self):
        """Run all demonstration scenarios."""
        print("\n" + "=" * 100)
        print(" " * 30 + "COST SHARING SYSTEM - COMPREHENSIVE DEMO")
        print("=" * 100)
        print("\nDemonstrating Shapley value-based cost allocation across multiple domains:")
        print("  1. Cloud Computing Infrastructure")
        print("  2. Rideshare Services")
        print("  3. Algorithm Performance")
        print("  4. Fairness Analysis")

        # Run all demos
        self.demo_cloud_cost_sharing()
        self.demo_rideshare_cost_sharing()
        self.demo_algorithm_comparison()
        self.demo_fairness_comparison()

        print("\n" + "=" * 100)
        print("ALL DEMOS COMPLETED")
        print("=" * 100)
        print(f"\nVisualizations saved to: {self.output_dir.absolute()}")
        print("\nKey Takeaways:")
        print("  • Shapley values provide fair, game-theoretically sound cost allocation")
        print("  • Accounts for marginal contributions and synergies")
        print("  • Guarantees efficiency, individual rationality, and (often) core stability")
        print("  • Applicable across diverse domains: cloud, rideshare, infrastructure, etc.")
        print("  • Monte Carlo approximation scales to large instances with high accuracy")
        print("\n" + "=" * 100)


if __name__ == '__main__':
    # Run comprehensive demonstration
    demo = CostSharingDemo(output_dir='visualization')
    demo.run_all_demos()
