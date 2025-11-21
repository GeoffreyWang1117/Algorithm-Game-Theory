"""
Cloud Computing Cost Sharing with Shapley Value

This module implements cost sharing mechanisms for cloud computing resources
using Shapley values. It models scenarios where multiple customers share
cloud infrastructure (compute, storage, network) and costs must be allocated fairly.

Real-World Applications:
    - AWS/Azure Reserved Instances cost allocation among departments
    - Multi-tenant SaaS platforms sharing infrastructure costs
    - Enterprise internal cloud chargeback systems
    - Shared database clusters cost distribution

Key Challenges:
    1. Fixed vs. variable costs (data center + per-instance costs)
    2. Economies of scale (bulk discounts)
    3. Peak vs. off-peak pricing
    4. Resource heterogeneity (different workload profiles)

References:
    - Nisan et al. (2007) "Algorithmic Game Theory" - Chapter on Cost Sharing
    - AWS Cost Allocation Best Practices
    - Googles' Borg paper on resource sharing
"""

from typing import Dict, List, Set, Tuple
import numpy as np
from dataclasses import dataclass
from shapley_value import ShapleyValue, ShapleyAnalyzer


@dataclass
class CloudResource:
    """Represents a cloud computing resource."""
    resource_type: str  # 'cpu', 'memory', 'storage', 'network'
    units: float  # Number of units (vCPUs, GB RAM, GB storage, Gbps)
    unit_price: float  # Price per unit
    fixed_cost: float = 0.0  # Fixed cost component


@dataclass
class Customer:
    """Represents a cloud customer with resource requirements."""
    id: str
    name: str
    cpu_cores: float  # vCPUs required
    memory_gb: float  # RAM in GB
    storage_gb: float  # Storage in GB
    network_gbps: float  # Network bandwidth in Gbps
    priority: int = 1  # 1=standard, 2=high-priority


class CloudCostModel:
    """
    Models cloud infrastructure cost with economies of scale.

    Cost Structure:
        1. Fixed costs: Data center, cooling, staff
        2. Variable costs: Per-resource pricing
        3. Economies of scale: Bulk discounts
        4. Peak pricing: Higher costs during peak hours
    """

    def __init__(self,
                 fixed_cost_monthly: float = 10000.0,
                 cpu_price_per_core: float = 30.0,
                 memory_price_per_gb: float = 5.0,
                 storage_price_per_gb: float = 0.1,
                 network_price_per_gbps: float = 100.0,
                 scale_discount_rate: float = 0.1):
        """
        Initialize cloud cost model.

        Args:
            fixed_cost_monthly: Monthly fixed costs (data center, etc.)
            cpu_price_per_core: Price per vCPU per month
            memory_price_per_gb: Price per GB RAM per month
            storage_price_per_gb: Price per GB storage per month
            network_price_per_gbps: Price per Gbps bandwidth per month
            scale_discount_rate: Discount rate for economies of scale (0.1 = 10%)
        """
        self.fixed_cost_monthly = fixed_cost_monthly
        self.cpu_price_per_core = cpu_price_per_core
        self.memory_price_per_gb = memory_price_per_gb
        self.storage_price_per_gb = storage_price_per_gb
        self.network_price_per_gbps = network_price_per_gbps
        self.scale_discount_rate = scale_discount_rate

    def compute_cost(self, customers: Set[str], customer_db: Dict[str, Customer]) -> float:
        """
        Compute total cost for a coalition of customers.

        Implements economies of scale: larger coalitions get bulk discounts.

        Args:
            customers: Set of customer IDs
            customer_db: Database mapping customer ID to Customer object

        Returns:
            Total monthly cost for the coalition
        """
        if not customers:
            return 0.0

        # Aggregate resource requirements
        total_cpu = 0.0
        total_memory = 0.0
        total_storage = 0.0
        total_network = 0.0

        for customer_id in customers:
            if customer_id in customer_db:
                customer = customer_db[customer_id]
                total_cpu += customer.cpu_cores
                total_memory += customer.memory_gb
                total_storage += customer.storage_gb
                total_network += customer.network_gbps

        # Compute variable costs
        variable_cost = (
            total_cpu * self.cpu_price_per_core +
            total_memory * self.memory_price_per_gb +
            total_storage * self.storage_price_per_gb +
            total_network * self.network_price_per_gbps
        )

        # Apply economies of scale discount
        # Discount increases with coalition size: discount = rate × log(1 + |S|)
        coalition_size = len(customers)
        scale_factor = 1.0 - self.scale_discount_rate * np.log1p(coalition_size) / np.log1p(10)
        scale_factor = max(0.5, scale_factor)  # Cap discount at 50%

        variable_cost *= scale_factor

        # Fixed costs are shared among all customers
        fixed_cost_share = self.fixed_cost_monthly

        total_cost = fixed_cost_share + variable_cost

        return total_cost


class CloudCostSharingSystem:
    """
    Complete cloud cost sharing system using Shapley values.

    Features:
        - Fair cost allocation based on marginal contributions
        - Handles heterogeneous workloads
        - Accounts for economies of scale
        - Verifies fairness properties
    """

    def __init__(self, customers: List[Customer], cost_model: CloudCostModel):
        """
        Initialize cost sharing system.

        Args:
            customers: List of Customer objects
            cost_model: CloudCostModel instance
        """
        self.customers = customers
        self.customer_db = {c.id: c for c in customers}
        self.cost_model = cost_model

        # Create cost function for Shapley value computation
        self.cost_function = lambda coalition: self.cost_model.compute_cost(
            coalition, self.customer_db
        )

        # Initialize Shapley calculator
        player_ids = [c.id for c in customers]
        self.shapley_calculator = ShapleyValue(player_ids, self.cost_function)
        self.analyzer = ShapleyAnalyzer(player_ids, self.cost_function)

    def allocate_costs(self, method: str = 'exact', num_samples: int = 1000) -> Dict[str, float]:
        """
        Allocate costs using Shapley values.

        Args:
            method: 'exact', 'monte_carlo', or 'incremental'
            num_samples: Number of samples for Monte Carlo

        Returns:
            Dictionary mapping customer ID to allocated cost
        """
        if method == 'exact':
            return self.shapley_calculator.exact()
        elif method == 'monte_carlo':
            return self.shapley_calculator.monte_carlo(num_samples=num_samples)
        elif method == 'incremental':
            return self.shapley_calculator.incremental(num_permutations=num_samples)
        else:
            raise ValueError(f"Unknown method: {method}")

    def analyze_allocation(self, allocation: Dict[str, float]) -> Dict:
        """
        Analyze the fairness and efficiency of the allocation.

        Args:
            allocation: Cost allocation from Shapley values

        Returns:
            Dictionary with analysis results
        """
        results = {}

        # 1. Efficiency
        results['is_efficient'] = self.analyzer.verify_efficiency(allocation)
        results['total_allocated'] = sum(allocation.values())
        results['total_cost'] = self.cost_function(set(allocation.keys()))

        # 2. Individual rationality
        results['individual_rationality'] = self.analyzer.verify_individual_rationality(allocation)

        # 3. Core membership
        is_in_core, blocking = self.analyzer.check_core_membership(allocation)
        results['is_in_core'] = is_in_core
        results['blocking_coalitions'] = blocking

        # 4. Savings
        results['savings'] = self.analyzer.compute_savings(allocation)
        results['cost_reduction_pct'] = self.analyzer.compute_cost_reduction_percentage(allocation)

        return results

    def get_allocation_summary(self, allocation: Dict[str, float]) -> str:
        """
        Generate human-readable summary of cost allocation.

        Args:
            allocation: Cost allocation

        Returns:
            Formatted summary string
        """
        lines = []
        lines.append("=" * 80)
        lines.append("CLOUD COST SHARING ALLOCATION SUMMARY")
        lines.append("=" * 80)

        # Total costs
        total_cost = sum(allocation.values())
        lines.append(f"\nTotal Monthly Cost: ${total_cost:,.2f}")
        lines.append(f"Number of Customers: {len(allocation)}")
        lines.append("")

        # Per-customer breakdown
        lines.append("Customer Allocations:")
        lines.append("-" * 80)
        lines.append(f"{'Customer ID':<20} {'Resources':<25} {'Allocated':<15} {'Standalone':<15} {'Savings'}")
        lines.append("-" * 80)

        for customer_id, allocated_cost in sorted(allocation.items()):
            customer = self.customer_db[customer_id]
            standalone = self.cost_function({customer_id})
            savings = standalone - allocated_cost
            savings_pct = (savings / standalone * 100) if standalone > 0 else 0

            resources = f"{customer.cpu_cores}CPU/{customer.memory_gb}GB"

            lines.append(
                f"{customer_id:<20} {resources:<25} "
                f"${allocated_cost:>12,.2f} ${standalone:>12,.2f} "
                f"${savings:>10,.2f} ({savings_pct:>5.1f}%)"
            )

        # Analysis
        analysis = self.analyze_allocation(allocation)

        lines.append("")
        lines.append("Fairness Analysis:")
        lines.append("-" * 80)
        lines.append(f"Efficiency (budget balance): {analysis['is_efficient']}")
        lines.append(f"Core membership (stability): {analysis['is_in_core']}")

        ir_all_satisfied = all(analysis['individual_rationality'].values())
        lines.append(f"Individual rationality: {ir_all_satisfied}")

        total_savings = sum(analysis['savings'].values())
        avg_reduction = np.mean(list(analysis['cost_reduction_pct'].values()))
        lines.append(f"\nTotal system savings: ${total_savings:,.2f}")
        lines.append(f"Average cost reduction: {avg_reduction:.1f}%")

        lines.append("=" * 80)

        return "\n".join(lines)


def create_example_scenario() -> CloudCostSharingSystem:
    """
    Create an example cloud cost sharing scenario.

    Scenario: 5 departments sharing corporate cloud infrastructure

    Returns:
        Configured CloudCostSharingSystem
    """
    # Define customers (departments)
    customers = [
        Customer(
            id='eng_team',
            name='Engineering Team',
            cpu_cores=32,
            memory_gb=128,
            storage_gb=2000,
            network_gbps=10,
            priority=2
        ),
        Customer(
            id='data_science',
            name='Data Science Team',
            cpu_cores=64,
            memory_gb=512,
            storage_gb=10000,
            network_gbps=20,
            priority=2
        ),
        Customer(
            id='web_services',
            name='Web Services',
            cpu_cores=16,
            memory_gb=64,
            storage_gb=500,
            network_gbps=50,
            priority=1
        ),
        Customer(
            id='analytics',
            name='Analytics Team',
            cpu_cores=24,
            memory_gb=192,
            storage_gb=5000,
            network_gbps=5,
            priority=1
        ),
        Customer(
            id='dev_test',
            name='Dev/Test Environment',
            cpu_cores=8,
            memory_gb=32,
            storage_gb=200,
            network_gbps=2,
            priority=1
        ),
    ]

    # Cloud cost model (based on AWS-like pricing)
    cost_model = CloudCostModel(
        fixed_cost_monthly=50000,  # Data center fixed costs
        cpu_price_per_core=30,     # ~$30/vCPU/month
        memory_price_per_gb=5,     # ~$5/GB/month
        storage_price_per_gb=0.1,  # ~$0.10/GB/month
        network_price_per_gbps=100,  # ~$100/Gbps/month
        scale_discount_rate=0.15   # 15% max discount for scale
    )

    return CloudCostSharingSystem(customers, cost_model)


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("CLOUD COST SHARING WITH SHAPLEY VALUES")
    print("=" * 80)

    # Create scenario
    system = create_example_scenario()

    print("\nScenario: Corporate Cloud Infrastructure Cost Sharing")
    print("5 departments sharing AWS-like infrastructure\n")

    # Show customer details
    print("Customer Resource Requirements:")
    print("-" * 80)
    print(f"{'Department':<25} {'CPU':<10} {'Memory':<12} {'Storage':<12} {'Network'}")
    print("-" * 80)
    for customer in system.customers:
        print(
            f"{customer.name:<25} {customer.cpu_cores:>6} cores "
            f"{customer.memory_gb:>8} GB {customer.storage_gb:>8} GB "
            f"{customer.network_gbps:>6} Gbps"
        )

    # Compute allocations using different methods
    print("\n" + "=" * 80)
    print("Computing Cost Allocations...")
    print("=" * 80)

    # Exact Shapley values
    print("\n1. Exact Shapley Values:")
    exact_allocation = system.allocate_costs(method='exact')
    print(system.get_allocation_summary(exact_allocation))

    # Monte Carlo approximation
    print("\n2. Monte Carlo Approximation (10,000 samples):")
    mc_allocation = system.allocate_costs(method='monte_carlo', num_samples=10000)

    print("\nComparison with Exact:")
    print("-" * 80)
    print(f"{'Customer':<20} {'Exact':<15} {'Monte Carlo':<15} {'Error'}")
    print("-" * 80)
    for customer_id in exact_allocation:
        exact = exact_allocation[customer_id]
        mc = mc_allocation[customer_id]
        error = abs(exact - mc)
        error_pct = (error / exact * 100) if exact > 0 else 0
        print(
            f"{customer_id:<20} ${exact:>12,.2f} ${mc:>12,.2f} "
            f"${error:>8,.2f} ({error_pct:>4.2f}%)"
        )

    # Comparison with naive allocation (proportional to resources)
    print("\n" + "=" * 80)
    print("Comparison: Shapley vs. Proportional Allocation")
    print("=" * 80)

    total_cost = system.cost_function(set(exact_allocation.keys()))

    # Proportional allocation based on total resource consumption
    total_resources = sum(
        c.cpu_cores * system.cost_model.cpu_price_per_core +
        c.memory_gb * system.cost_model.memory_price_per_gb +
        c.storage_gb * system.cost_model.storage_price_per_gb +
        c.network_gbps * system.cost_model.network_price_per_gbps
        for c in system.customers
    )

    proportional_allocation = {}
    for customer in system.customers:
        customer_resources = (
            customer.cpu_cores * system.cost_model.cpu_price_per_core +
            customer.memory_gb * system.cost_model.memory_price_per_gb +
            customer.storage_gb * system.cost_model.storage_price_per_gb +
            customer.network_gbps * system.cost_model.network_price_per_gbps
        )
        proportional_allocation[customer.id] = total_cost * (customer_resources / total_resources)

    print(f"\n{'Customer':<20} {'Shapley':<15} {'Proportional':<15} {'Difference'}")
    print("-" * 80)
    for customer_id in exact_allocation:
        shapley = exact_allocation[customer_id]
        proportional = proportional_allocation[customer_id]
        diff = shapley - proportional
        print(
            f"{customer_id:<20} ${shapley:>12,.2f} ${proportional:>12,.2f} "
            f"${diff:>12,.2f}"
        )

    print("\nKey Insight:")
    print("Shapley allocation accounts for marginal contributions and synergies,")
    print("while proportional allocation only considers resource consumption.")
    print("Shapley is fairer as it rewards customers who enable others to join.")

    print("\n" + "=" * 80)
