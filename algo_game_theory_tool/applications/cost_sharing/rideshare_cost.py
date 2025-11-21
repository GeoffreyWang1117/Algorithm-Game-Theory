"""
Rideshare Cost Allocation with Shapley Value

This module implements fair cost allocation for ridesharing services (Uber Pool,
Lyft Shared, etc.) using Shapley values. It handles route optimization and
ensures each rider pays based on their marginal contribution to the total cost.

Real-World Applications:
    - Uber Pool / Lyft Shared ride cost splitting
    - Corporate shuttle services
    - Carpool matching platforms
    - Delivery route cost allocation

Key Challenges:
    1. Route optimization (TSP-like problem)
    2. Detour costs: Extra distance to pick up other riders
    3. Fairness: Riders who cause more detours should pay more
    4. Dynamic pricing: Peak hours, demand surge

Mathematical Model:
    - Cost function: c(S) = base_fare + distance(optimal_route(S)) × price_per_mile
    - Shapley value fairly distributes c(N) among all riders
    - Each rider pays for their marginal impact on the route

References:
    - Shapley (1953) "A value for n-person games"
    - Uber Pool pricing methodology
    - Kamar & Horvitz (2009) "Collaboration and shared plans in the open world"
"""

from typing import List, Set, Tuple, Dict
import numpy as np
from dataclasses import dataclass
from itertools import permutations
import matplotlib.pyplot as plt
from shapley_value import ShapleyValue, ShapleyAnalyzer


@dataclass
class Location:
    """Represents a geographic location."""
    name: str
    lat: float  # Latitude
    lon: float  # Longitude

    def distance_to(self, other: 'Location') -> float:
        """
        Compute Euclidean distance to another location.

        In practice, would use Haversine formula for lat/lon coordinates.
        For simplicity, we use Euclidean distance scaled to approximate miles.
        """
        # Approximate: 1 degree ≈ 69 miles
        lat_diff = (self.lat - other.lat) * 69
        lon_diff = (self.lon - other.lon) * 69 * np.cos(np.radians((self.lat + other.lat) / 2))

        return np.sqrt(lat_diff**2 + lon_diff**2)


@dataclass
class Rider:
    """Represents a rideshare passenger."""
    id: str
    name: str
    pickup: Location
    dropoff: Location
    max_detour_miles: float = 5.0  # Maximum acceptable detour
    time_flexibility: float = 1.0  # Flexibility score (0-1)


class RideRoutePlanner:
    """
    Plan optimal routes for rideshare groups.

    Simplified TSP solver for demonstration.
    In production, would use Google Maps API / OSRM for actual routing.
    """

    def __init__(self, origin: Location):
        """
        Initialize route planner.

        Args:
            origin: Starting location (driver's initial position)
        """
        self.origin = origin

    def compute_route_distance(self, riders: Set[str], rider_db: Dict[str, Rider]) -> float:
        """
        Compute total distance for optimal route serving given riders.

        Algorithm:
            1. Find optimal order to pick up all riders
            2. Then drop off all riders in optimal order
            3. Return total distance

        Simplified version: Use greedy nearest-neighbor heuristic.

        Args:
            riders: Set of rider IDs
            rider_db: Database mapping rider ID to Rider object

        Returns:
            Total route distance in miles
        """
        if not riders:
            return 0.0

        # Get rider objects
        rider_list = [rider_db[rid] for rid in riders if rid in rider_db]

        if not rider_list:
            return 0.0

        # Simplified routing: pick up all riders, then drop off all riders
        # More realistic would interleave pickups and dropoffs

        total_distance = 0.0
        current_location = self.origin

        # Phase 1: Pick up all riders (greedy nearest-neighbor)
        remaining_pickups = [r.pickup for r in rider_list]

        while remaining_pickups:
            # Find nearest pickup
            nearest = min(remaining_pickups, key=lambda loc: current_location.distance_to(loc))
            total_distance += current_location.distance_to(nearest)
            current_location = nearest
            remaining_pickups.remove(nearest)

        # Phase 2: Drop off all riders (greedy nearest-neighbor)
        remaining_dropoffs = [r.dropoff for r in rider_list]

        while remaining_dropoffs:
            # Find nearest dropoff
            nearest = min(remaining_dropoffs, key=lambda loc: current_location.distance_to(loc))
            total_distance += current_location.distance_to(nearest)
            current_location = nearest
            remaining_dropoffs.remove(nearest)

        return total_distance

    def compute_optimal_route_exact(self, riders: Set[str], rider_db: Dict[str, Rider]) -> Tuple[float, List]:
        """
        Compute exact optimal route using brute force (small n only).

        For demonstration purposes. Real systems use sophisticated algorithms.

        Args:
            riders: Set of rider IDs
            rider_db: Database

        Returns:
            Tuple of (min_distance, optimal_order)
        """
        if not riders or len(riders) > 8:
            # Fall back to greedy for large instances
            distance = self.compute_route_distance(riders, rider_db)
            return distance, list(riders)

        rider_list = [rider_db[rid] for rid in riders if rid in rider_db]

        min_distance = float('inf')
        optimal_order = None

        # Try all permutations of pickup/dropoff orders
        # Simplified: just try all pickup orders, then all dropoff orders
        for pickup_order in permutations(rider_list):
            total_distance = 0.0
            current_location = self.origin

            # Pick up in this order
            for rider in pickup_order:
                total_distance += current_location.distance_to(rider.pickup)
                current_location = rider.pickup

            # Drop off in same order (could optimize this too)
            for rider in pickup_order:
                total_distance += current_location.distance_to(rider.dropoff)
                current_location = rider.dropoff

            if total_distance < min_distance:
                min_distance = total_distance
                optimal_order = [r.id for r in pickup_order]

        return min_distance, optimal_order


class RideshareCostModel:
    """
    Models rideshare cost with base fare and per-mile pricing.

    Pricing Components:
        - Base fare: Minimum charge for any ride
        - Per-mile rate: Cost per mile traveled
        - Time-based surge: Multiplier during peak hours
    """

    def __init__(self,
                 base_fare: float = 5.0,
                 price_per_mile: float = 1.5,
                 surge_multiplier: float = 1.0):
        """
        Initialize rideshare cost model.

        Args:
            base_fare: Base fare for the ride ($)
            price_per_mile: Cost per mile ($)
            surge_multiplier: Surge pricing multiplier (1.0 = no surge)
        """
        self.base_fare = base_fare
        self.price_per_mile = price_per_mile
        self.surge_multiplier = surge_multiplier

    def compute_cost(self, distance: float) -> float:
        """
        Compute total cost for a given route distance.

        Args:
            distance: Total route distance in miles

        Returns:
            Total cost in dollars
        """
        if distance <= 0:
            return 0.0

        cost = self.base_fare + distance * self.price_per_mile
        cost *= self.surge_multiplier

        return cost


class RideshareCostSharingSystem:
    """
    Complete rideshare cost sharing system using Shapley values.

    Workflow:
        1. Plan optimal route for rider group
        2. Compute total cost
        3. Use Shapley values to fairly allocate cost
        4. Each rider pays based on marginal contribution
    """

    def __init__(self,
                 riders: List[Rider],
                 origin: Location,
                 cost_model: RideshareCostModel):
        """
        Initialize rideshare cost sharing system.

        Args:
            riders: List of Rider objects
            origin: Driver's starting location
            cost_model: Pricing model
        """
        self.riders = riders
        self.rider_db = {r.id: r for r in riders}
        self.origin = origin
        self.cost_model = cost_model
        self.route_planner = RideRoutePlanner(origin)

        # Create cost function for Shapley calculation
        def rideshare_cost(coalition: Set[str]) -> float:
            if not coalition:
                return 0.0
            distance = self.route_planner.compute_route_distance(coalition, self.rider_db)
            return self.cost_model.compute_cost(distance)

        self.cost_function = rideshare_cost

        # Initialize Shapley calculator
        rider_ids = [r.id for r in riders]
        self.shapley_calculator = ShapleyValue(rider_ids, self.cost_function)
        self.analyzer = ShapleyAnalyzer(rider_ids, self.cost_function)

    def allocate_costs(self, method: str = 'exact', num_samples: int = 5000) -> Dict[str, float]:
        """
        Allocate ride cost using Shapley values.

        Args:
            method: 'exact', 'monte_carlo', or 'incremental'
            num_samples: Number of samples for approximation methods

        Returns:
            Dictionary mapping rider ID to allocated cost
        """
        if method == 'exact' and len(self.riders) <= 10:
            return self.shapley_calculator.exact()
        elif method == 'monte_carlo':
            return self.shapley_calculator.monte_carlo(num_samples=num_samples, seed=42)
        else:
            return self.shapley_calculator.incremental(num_permutations=num_samples, seed=42)

    def analyze_allocation(self, allocation: Dict[str, float]) -> Dict:
        """Analyze fairness of allocation."""
        results = {}

        results['is_efficient'] = self.analyzer.verify_efficiency(allocation)
        results['total_allocated'] = sum(allocation.values())
        results['total_cost'] = self.cost_function(set(allocation.keys()))

        results['individual_rationality'] = self.analyzer.verify_individual_rationality(allocation)
        results['savings'] = self.analyzer.compute_savings(allocation)
        results['cost_reduction_pct'] = self.analyzer.compute_cost_reduction_percentage(allocation)

        # Compute individual ride distances
        results['solo_distances'] = {}
        for rider_id in allocation:
            rider = self.rider_db[rider_id]
            solo_distance = self.origin.distance_to(rider.pickup) + \
                          rider.pickup.distance_to(rider.dropoff)
            results['solo_distances'][rider_id] = solo_distance

        return results

    def visualize_allocation(self, allocation: Dict[str, float], save_path: str = None):
        """
        Visualize cost allocation compared to solo rides.

        Args:
            allocation: Shapley cost allocation
            save_path: Optional path to save figure
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Plot 1: Cost comparison
        rider_ids = list(allocation.keys())
        shapley_costs = [allocation[rid] for rid in rider_ids]
        solo_costs = [self.cost_function({rid}) for rid in rider_ids]

        x = np.arange(len(rider_ids))
        width = 0.35

        axes[0].bar(x - width/2, solo_costs, width, label='Solo Ride Cost', alpha=0.8)
        axes[0].bar(x + width/2, shapley_costs, width, label='Shared Ride Cost (Shapley)', alpha=0.8)

        axes[0].set_xlabel('Rider')
        axes[0].set_ylabel('Cost ($)')
        axes[0].set_title('Cost Comparison: Solo vs. Shared Ride')
        axes[0].set_xticks(x)
        axes[0].set_xticklabels([self.rider_db[rid].name for rid in rider_ids], rotation=45)
        axes[0].legend()
        axes[0].grid(axis='y', alpha=0.3)

        # Plot 2: Savings
        savings = [solo_costs[i] - shapley_costs[i] for i in range(len(rider_ids))]
        colors = ['green' if s > 0 else 'red' for s in savings]

        axes[1].bar(x, savings, color=colors, alpha=0.7)
        axes[1].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        axes[1].set_xlabel('Rider')
        axes[1].set_ylabel('Savings ($)')
        axes[1].set_title('Savings from Ridesharing')
        axes[1].set_xticks(x)
        axes[1].set_xticklabels([self.rider_db[rid].name for rid in rider_ids], rotation=45)
        axes[1].grid(axis='y', alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Visualization saved to {save_path}")
        else:
            plt.show()

        return fig

    def get_allocation_summary(self, allocation: Dict[str, float]) -> str:
        """Generate human-readable allocation summary."""
        lines = []
        lines.append("=" * 90)
        lines.append("RIDESHARE COST ALLOCATION SUMMARY (Shapley Value)")
        lines.append("=" * 90)

        # Total cost
        total_cost = sum(allocation.values())
        total_route_distance = self.route_planner.compute_route_distance(
            set(allocation.keys()), self.rider_db
        )

        lines.append(f"\nTotal Ride Cost: ${total_cost:.2f}")
        lines.append(f"Total Route Distance: {total_route_distance:.2f} miles")
        lines.append(f"Number of Riders: {len(allocation)}")
        lines.append("")

        # Per-rider breakdown
        lines.append("Rider Allocations:")
        lines.append("-" * 90)
        lines.append(f"{'Rider':<20} {'Route':<30} {'Allocated':<12} {'Solo Cost':<12} {'Savings'}")
        lines.append("-" * 90)

        analysis = self.analyze_allocation(allocation)

        for rider_id in sorted(allocation.keys()):
            rider = self.rider_db[rider_id]
            allocated = allocation[rider_id]
            solo_cost = self.cost_function({rider_id})
            savings = solo_cost - allocated
            savings_pct = (savings / solo_cost * 100) if solo_cost > 0 else 0

            route_str = f"{rider.pickup.name[:12]} → {rider.dropoff.name[:12]}"

            lines.append(
                f"{rider.name:<20} {route_str:<30} "
                f"${allocated:>9.2f} ${solo_cost:>9.2f} "
                f"${savings:>7.2f} ({savings_pct:>4.1f}%)"
            )

        # Summary statistics
        total_savings = sum(analysis['savings'].values())
        avg_savings_pct = np.mean(list(analysis['cost_reduction_pct'].values()))

        lines.append("")
        lines.append("Summary:")
        lines.append("-" * 90)
        lines.append(f"Total savings from ridesharing: ${total_savings:.2f}")
        lines.append(f"Average cost reduction: {avg_savings_pct:.1f}%")
        lines.append(f"Efficiency (budget balance): {analysis['is_efficient']}")

        ir_all = all(analysis['individual_rationality'].values())
        lines.append(f"Individual rationality: {ir_all} (all riders save money)")

        lines.append("=" * 90)

        return "\n".join(lines)


def create_example_scenario() -> RideshareCostSharingSystem:
    """
    Create an example rideshare scenario.

    Scenario: 4 coworkers sharing a ride to the office

    Returns:
        Configured RideshareCostSharingSystem
    """
    # Origin: Residential area
    origin = Location("Downtown Pickup Point", lat=37.7749, lon=-122.4194)

    # Define riders
    riders = [
        Rider(
            id='alice',
            name='Alice',
            pickup=Location("Alice Home", lat=37.7849, lon=-122.4094),
            dropoff=Location("Office Building A", lat=37.7949, lon=-122.3994),
            max_detour_miles=3.0
        ),
        Rider(
            id='bob',
            name='Bob',
            pickup=Location("Bob Home", lat=37.7649, lon=-122.4294),
            dropoff=Location("Office Building A", lat=37.7949, lon=-122.3994),
            max_detour_miles=5.0
        ),
        Rider(
            id='carol',
            name='Carol',
            pickup=Location("Carol Home", lat=37.7749, lon=-122.4394),
            dropoff=Location("Office Building B", lat=37.7999, lon=-122.3944),
            max_detour_miles=4.0
        ),
        Rider(
            id='dave',
            name='Dave',
            pickup=Location("Dave Home", lat=37.7949, lon=-122.4244),
            dropoff=Location("Office Building A", lat=37.7949, lon=-122.3994),
            max_detour_miles=6.0
        ),
    ]

    # Cost model (Uber-like pricing)
    cost_model = RideshareCostModel(
        base_fare=5.0,
        price_per_mile=1.5,
        surge_multiplier=1.0  # No surge
    )

    return RideshareCostSharingSystem(riders, origin, cost_model)


if __name__ == '__main__':
    print("\n" + "=" * 90)
    print("RIDESHARE COST ALLOCATION WITH SHAPLEY VALUES")
    print("=" * 90)

    # Create scenario
    system = create_example_scenario()

    print("\nScenario: 4 coworkers sharing morning commute")
    print("Base fare: $5.00, Rate: $1.50/mile, Surge: 1.0x\n")

    # Show rider details
    print("Riders:")
    print("-" * 90)
    for rider in system.riders:
        solo_distance = system.origin.distance_to(rider.pickup) + \
                       rider.pickup.distance_to(rider.dropoff)
        solo_cost = system.cost_function({rider.id})
        print(f"{rider.name:<10} {rider.pickup.name:<20} → {rider.dropoff.name:<20} "
              f"(Solo: {solo_distance:.1f}mi, ${solo_cost:.2f})")

    # Compute allocation
    print("\n" + "=" * 90)
    print("Computing Shapley Value Allocation...")
    print("=" * 90)

    allocation = system.allocate_costs(method='exact')
    print(system.get_allocation_summary(allocation))

    # Compare with equal split
    print("\n" + "=" * 90)
    print("Comparison: Shapley vs. Equal Split")
    print("=" * 90)

    total_cost = sum(allocation.values())
    equal_split = {rid: total_cost / len(allocation) for rid in allocation}

    print(f"\n{'Rider':<20} {'Shapley':<15} {'Equal Split':<15} {'Difference'}")
    print("-" * 70)
    for rider_id in allocation:
        shapley = allocation[rider_id]
        equal = equal_split[rider_id]
        diff = shapley - equal
        rider_name = system.rider_db[rider_id].name

        print(f"{rider_name:<20} ${shapley:>12.2f} ${equal:>12.2f} ${diff:>12.2f}")

    print("\nKey Insight:")
    print("Shapley allocation accounts for each rider's marginal contribution to route cost.")
    print("Riders who cause more detours or are picked up earlier pay slightly more.")
    print("This is fairer than equal split, as it reflects actual cost causation.")

    print("\n" + "=" * 90)
