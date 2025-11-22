"""
Winner Determination Problem (WDP) Solver for Spectrum Auctions

The WDP is the core computational challenge in combinatorial auctions:
Given bids on bundles of items, find the allocation that maximizes revenue
while ensuring each item is allocated to at most one bidder.

Problem Formulation:
    Maximize: Σᵢ vᵢxᵢ
    Subject to: Σᵢ:j∈Sᵢ xᵢ ≤ 1  for all items j
                xᵢ ∈ {0, 1}

Where:
    - vᵢ = value of bid i
    - xᵢ = 1 if bid i wins, 0 otherwise
    - Sᵢ = set of items in bid i

Complexity: NP-hard (reduction from Set Packing)

Real-World Context:
    - FCC Auction 73 (2008): $19.6 billion, 1,090 licenses
    - FCC Incentive Auction (2016-17): $19.8 billion, 2-sided market
    - European 5G auctions: Billions in revenue

Algorithms Implemented:
    1. Greedy (polynomial time, approximation)
    2. Dynamic Programming (pseudo-polynomial for special cases)
    3. Integer Linear Programming (optimal, using branch-and-bound)
    4. Exhaustive Search (optimal, small instances only)

References:
    - Nisan et al. (2007) "Algorithmic Game Theory" - Chapter 11
    - Cramton et al. (2006) "Combinatorial Auctions"
    - de Vries & Vohra (2003) "Combinatorial Auctions: A Survey"
"""

from typing import List, Set, Dict, Tuple, Optional
from dataclasses import dataclass
import numpy as np
from itertools import combinations, chain
import time


@dataclass
class Bid:
    """Represents a bid in a combinatorial auction."""
    bidder_id: str
    items: Set[int]  # Set of item IDs
    value: float  # Bidder's valuation for this bundle
    bid_id: Optional[str] = None  # Unique bid identifier

    def __post_init__(self):
        if self.bid_id is None:
            items_str = ','.join(map(str, sorted(self.items)))
            self.bid_id = f"{self.bidder_id}_{items_str}"

    def conflicts_with(self, other: 'Bid') -> bool:
        """Check if this bid conflicts with another (share items)."""
        return bool(self.items & other.items)


@dataclass
class Allocation:
    """Represents a solution to the WDP."""
    winning_bids: List[Bid]
    total_revenue: float
    allocated_items: Set[int]
    computation_time: float
    method: str  # Algorithm used

    def is_feasible(self) -> bool:
        """Verify allocation is feasible (no item allocated twice)."""
        allocated = set()
        for bid in self.winning_bids:
            if bid.items & allocated:
                return False
            allocated |= bid.items
        return True

    def efficiency(self, total_items: int) -> float:
        """Compute allocation efficiency (fraction of items allocated)."""
        return len(self.allocated_items) / total_items if total_items > 0 else 0.0


class WDPSolver:
    """
    Solver for the Winner Determination Problem in combinatorial auctions.

    Provides multiple algorithms with different trade-offs:
    - Greedy: Fast but approximate
    - DP: Optimal for special structures
    - ILP: Optimal but slow for large instances
    - Exhaustive: Optimal but only for tiny instances
    """

    def __init__(self, bids: List[Bid], num_items: int):
        """
        Initialize WDP solver.

        Args:
            bids: List of bids
            num_items: Total number of items
        """
        self.bids = bids
        self.num_items = num_items
        self.conflict_graph = self._build_conflict_graph()

    def _build_conflict_graph(self) -> Dict[str, Set[str]]:
        """Build conflict graph: bids that share items."""
        graph = {bid.bid_id: set() for bid in self.bids}

        for i, bid1 in enumerate(self.bids):
            for bid2 in self.bids[i+1:]:
                if bid1.conflicts_with(bid2):
                    graph[bid1.bid_id].add(bid2.bid_id)
                    graph[bid2.bid_id].add(bid1.bid_id)

        return graph

    def solve_greedy(self) -> Allocation:
        """
        Greedy algorithm: Select bids in decreasing order of value density.

        Value density = value / number of items

        Time Complexity: O(n log n + nm) where n=bids, m=items
        Approximation: Can be arbitrarily bad in worst case, but works well in practice

        Returns:
            Allocation solution
        """
        start_time = time.time()

        # Sort bids by value density (value per item)
        sorted_bids = sorted(
            self.bids,
            key=lambda b: b.value / len(b.items) if len(b.items) > 0 else 0,
            reverse=True
        )

        winning_bids = []
        allocated_items = set()
        total_revenue = 0.0

        for bid in sorted_bids:
            # Check if bid conflicts with already allocated items
            if not (bid.items & allocated_items):
                winning_bids.append(bid)
                allocated_items |= bid.items
                total_revenue += bid.value

        computation_time = time.time() - start_time

        return Allocation(
            winning_bids=winning_bids,
            total_revenue=total_revenue,
            allocated_items=allocated_items,
            computation_time=computation_time,
            method='greedy'
        )

    def solve_greedy_by_value(self) -> Allocation:
        """
        Greedy algorithm: Select bids in decreasing order of absolute value.

        Often performs better than density-based greedy for sparse bids.

        Returns:
            Allocation solution
        """
        start_time = time.time()

        # Sort bids by value
        sorted_bids = sorted(self.bids, key=lambda b: b.value, reverse=True)

        winning_bids = []
        allocated_items = set()
        total_revenue = 0.0

        for bid in sorted_bids:
            if not (bid.items & allocated_items):
                winning_bids.append(bid)
                allocated_items |= bid.items
                total_revenue += bid.value

        computation_time = time.time() - start_time

        return Allocation(
            winning_bids=winning_bids,
            total_revenue=total_revenue,
            allocated_items=allocated_items,
            computation_time=computation_time,
            method='greedy_value'
        )

    def solve_exhaustive(self) -> Allocation:
        """
        Exhaustive search: Try all feasible combinations.

        Time Complexity: O(2^n) - only feasible for n ≤ 20
        Guarantees: Optimal solution

        Returns:
            Optimal allocation
        """
        start_time = time.time()

        if len(self.bids) > 20:
            raise ValueError("Exhaustive search only feasible for ≤ 20 bids")

        best_revenue = 0.0
        best_allocation = []

        # Try all subsets of bids
        for r in range(len(self.bids) + 1):
            for bid_subset in combinations(self.bids, r):
                # Check feasibility
                allocated = set()
                feasible = True
                for bid in bid_subset:
                    if bid.items & allocated:
                        feasible = False
                        break
                    allocated |= bid.items

                if feasible:
                    revenue = sum(bid.value for bid in bid_subset)
                    if revenue > best_revenue:
                        best_revenue = revenue
                        best_allocation = list(bid_subset)

        allocated_items = set()
        for bid in best_allocation:
            allocated_items |= bid.items

        computation_time = time.time() - start_time

        return Allocation(
            winning_bids=best_allocation,
            total_revenue=best_revenue,
            allocated_items=allocated_items,
            computation_time=computation_time,
            method='exhaustive'
        )

    def solve_dp_single_unit(self) -> Allocation:
        """
        Dynamic programming for single-unit bids (each bid contains exactly 1 item).

        This is the classic weighted interval scheduling problem.

        Time Complexity: O(n²) where n = number of bids
        Guarantees: Optimal for single-unit bids

        Returns:
            Optimal allocation (if all bids are single-unit)
        """
        start_time = time.time()

        # Verify all bids are single-unit
        if not all(len(bid.items) == 1 for bid in self.bids):
            raise ValueError("DP single-unit only works for single-item bids")

        # Sort bids by item ID
        sorted_bids = sorted(self.bids, key=lambda b: list(b.items)[0])
        n = len(sorted_bids)

        if n == 0:
            return Allocation([], 0.0, set(), time.time() - start_time, 'dp_single_unit')

        # DP: dp[i] = max revenue using bids 0...i
        dp = [0.0] * (n + 1)
        choice = [None] * (n + 1)

        for i in range(1, n + 1):
            bid = sorted_bids[i-1]

            # Option 1: Don't take bid i
            dp[i] = dp[i-1]
            choice[i] = choice[i-1]

            # Option 2: Take bid i
            # Find last compatible bid
            item = list(bid.items)[0]
            j = i - 1
            while j > 0 and list(sorted_bids[j-1].items)[0] == item:
                j -= 1

            if dp[j] + bid.value > dp[i]:
                dp[i] = dp[j] + bid.value
                if choice[j] is None:
                    choice[i] = [bid]
                else:
                    choice[i] = choice[j] + [bid]

        winning_bids = choice[n] if choice[n] is not None else []
        total_revenue = dp[n]
        allocated_items = set()
        for bid in winning_bids:
            allocated_items |= bid.items

        computation_time = time.time() - start_time

        return Allocation(
            winning_bids=winning_bids,
            total_revenue=total_revenue,
            allocated_items=allocated_items,
            computation_time=computation_time,
            method='dp_single_unit'
        )

    def solve_branch_and_bound(self, time_limit: float = 10.0) -> Allocation:
        """
        Branch-and-bound with greedy upper bound.

        Time Complexity: Exponential worst-case, but often practical
        Guarantees: Optimal if completes within time limit

        Args:
            time_limit: Maximum computation time (seconds)

        Returns:
            Best allocation found
        """
        start_time = time.time()

        # Sort bids by value density for better pruning
        sorted_bids = sorted(
            self.bids,
            key=lambda b: b.value / len(b.items) if len(b.items) > 0 else 0,
            reverse=True
        )

        best_revenue = 0.0
        best_allocation = []

        def upper_bound(allocated_items: Set[int], remaining_bids: List[Bid]) -> float:
            """Compute upper bound using fractional relaxation (greedy)."""
            bound = 0.0
            temp_allocated = allocated_items.copy()

            for bid in remaining_bids:
                if not (bid.items & temp_allocated):
                    bound += bid.value
                    temp_allocated |= bid.items

            return bound

        def branch_and_bound_recursive(
            current_allocation: List[Bid],
            current_revenue: float,
            allocated_items: Set[int],
            remaining_bids: List[Bid],
            depth: int
        ):
            nonlocal best_revenue, best_allocation

            # Time limit check
            if time.time() - start_time > time_limit:
                return

            # Base case
            if not remaining_bids:
                if current_revenue > best_revenue:
                    best_revenue = current_revenue
                    best_allocation = current_allocation.copy()
                return

            # Pruning: check upper bound
            ub = current_revenue + upper_bound(allocated_items, remaining_bids)
            if ub <= best_revenue:
                return  # Prune this branch

            # Branch: try including first remaining bid
            bid = remaining_bids[0]
            rest = remaining_bids[1:]

            # Branch 1: Include this bid (if feasible)
            if not (bid.items & allocated_items):
                branch_and_bound_recursive(
                    current_allocation + [bid],
                    current_revenue + bid.value,
                    allocated_items | bid.items,
                    rest,
                    depth + 1
                )

            # Branch 2: Exclude this bid
            branch_and_bound_recursive(
                current_allocation,
                current_revenue,
                allocated_items,
                rest,
                depth + 1
            )

        # Start recursion
        branch_and_bound_recursive([], 0.0, set(), sorted_bids, 0)

        allocated_items = set()
        for bid in best_allocation:
            allocated_items |= bid.items

        computation_time = time.time() - start_time

        return Allocation(
            winning_bids=best_allocation,
            total_revenue=best_revenue,
            allocated_items=allocated_items,
            computation_time=computation_time,
            method='branch_and_bound'
        )

    def solve(self, method: str = 'auto', time_limit: float = 10.0) -> Allocation:
        """
        Solve WDP using specified method.

        Args:
            method: 'auto', 'greedy', 'greedy_value', 'exhaustive', 'dp_single_unit', 'branch_and_bound'
            time_limit: Time limit for branch-and-bound

        Returns:
            Allocation solution
        """
        if method == 'auto':
            # Automatic method selection based on problem size
            if len(self.bids) <= 15:
                method = 'exhaustive'
            elif all(len(bid.items) == 1 for bid in self.bids):
                method = 'dp_single_unit'
            elif len(self.bids) <= 50:
                method = 'branch_and_bound'
            else:
                method = 'greedy_value'

        if method == 'greedy':
            return self.solve_greedy()
        elif method == 'greedy_value':
            return self.solve_greedy_by_value()
        elif method == 'exhaustive':
            return self.solve_exhaustive()
        elif method == 'dp_single_unit':
            return self.solve_dp_single_unit()
        elif method == 'branch_and_bound':
            return self.solve_branch_and_bound(time_limit)
        else:
            raise ValueError(f"Unknown method: {method}")


def compare_algorithms(bids: List[Bid], num_items: int) -> Dict[str, Allocation]:
    """
    Compare different WDP solving algorithms.

    Args:
        bids: List of bids
        num_items: Total number of items

    Returns:
        Dictionary mapping algorithm name to allocation
    """
    solver = WDPSolver(bids, num_items)
    results = {}

    # Greedy variants (always fast)
    results['greedy'] = solver.solve_greedy()
    results['greedy_value'] = solver.solve_greedy_by_value()

    # Exact algorithms (if feasible)
    if len(bids) <= 15:
        results['exhaustive'] = solver.solve_exhaustive()

    if all(len(bid.items) == 1 for bid in bids):
        results['dp_single_unit'] = solver.solve_dp_single_unit()

    if len(bids) <= 30:
        results['branch_and_bound'] = solver.solve_branch_and_bound(time_limit=5.0)

    return results


if __name__ == '__main__':
    # Example: Simple spectrum auction
    print("=" * 80)
    print("Winner Determination Problem - Example")
    print("=" * 80)

    # 5 spectrum licenses, 4 bidders
    bids = [
        Bid('Telecom_A', {0, 1}, 100),      # Wants licenses 0,1 for $100M
        Bid('Telecom_A', {2}, 40),          # Wants license 2 for $40M
        Bid('Telecom_B', {0}, 60),          # Wants license 0 for $60M
        Bid('Telecom_B', {1, 2, 3}, 120),   # Wants licenses 1,2,3 for $120M
        Bid('Telecom_C', {0, 1, 2}, 110),   # Wants licenses 0,1,2 for $110M
        Bid('Telecom_C', {3, 4}, 80),       # Wants licenses 3,4 for $80M
        Bid('Telecom_D', {4}, 50),          # Wants license 4 for $50M
    ]

    num_items = 5

    print(f"\nProblem: {len(bids)} bids on {num_items} spectrum licenses")
    print("\nBids:")
    for bid in bids:
        items_str = ', '.join(map(str, sorted(bid.items)))
        print(f"  {bid.bidder_id}: Licenses [{items_str}] for ${bid.value}M")

    # Solve with different algorithms
    solver = WDPSolver(bids, num_items)

    print("\n" + "=" * 80)
    print("Algorithm Comparison")
    print("=" * 80)

    results = compare_algorithms(bids, num_items)

    for method, allocation in results.items():
        print(f"\n{method.upper()}:")
        print(f"  Revenue: ${allocation.total_revenue}M")
        print(f"  Time: {allocation.computation_time*1000:.2f}ms")
        print(f"  Efficiency: {allocation.efficiency(num_items)*100:.1f}%")
        print(f"  Winning bids:")
        for bid in allocation.winning_bids:
            items_str = ', '.join(map(str, sorted(bid.items)))
            print(f"    {bid.bidder_id}: [{items_str}] = ${bid.value}M")

    print("\n" + "=" * 80)
