"""
Shapley Value Calculation Algorithms

This module implements various algorithms for computing the Shapley value,
a solution concept in cooperative game theory that fairly distributes the
total value (or cost) among players based on their marginal contributions.

Mathematical Definition:
    φᵢ(v) = Σ_{S⊆N\{i}} [|S|!(n-|S|-1)! / n!] × [v(S∪{i}) - v(S)]

Where:
    - N is the set of all players
    - v is the characteristic function: v(S) = value of coalition S
    - φᵢ(v) is the Shapley value for player i

Properties:
    1. Efficiency: Σᵢφᵢ(v) = v(N) (全部价值被分配)
    2. Symmetry: 对称玩家获得相同价值
    3. Dummy: 虚拟玩家获得0价值
    4. Additivity: 线性可加性

Applications:
    - Cloud computing resource cost sharing
    - Rideshare cost allocation
    - Voting power analysis
    - Feature importance in ML (SHAP values)

References:
    - Shapley, L. S. (1953). "A value for n-person games"
    - Roth, A. E. (1988). "The Shapley value: essays in honor of Lloyd S. Shapley"
"""

from typing import Callable, List, Dict, Set, FrozenSet, Tuple
from itertools import combinations, permutations
import numpy as np
from collections import defaultdict
import math


class ShapleyValue:
    """
    Compute Shapley values for cooperative games.

    The characteristic function v(S) can represent either:
    - Value function: v(S) = total value of coalition S
    - Cost function: c(S) = total cost of coalition S

    For cost sharing, we use the cost function and compute Shapley costs.
    """

    def __init__(self, players: List[str], cost_function: Callable[[Set[str]], float]):
        """
        Initialize Shapley value calculator.

        Args:
            players: List of player identifiers
            cost_function: Function that takes a set of players and returns cost/value
        """
        self.players = players
        self.n = len(players)
        self.cost_function = cost_function

        # Cache for computed coalition costs
        self._cost_cache: Dict[FrozenSet[str], float] = {}

    def _get_cost(self, coalition: Set[str]) -> float:
        """Get cost with caching."""
        frozen = frozenset(coalition)
        if frozen not in self._cost_cache:
            self._cost_cache[frozen] = self.cost_function(coalition)
        return self._cost_cache[frozen]

    def exact(self) -> Dict[str, float]:
        """
        Compute exact Shapley values using the definition.

        Time Complexity: O(2^n × n)
        Space Complexity: O(2^n)

        Only feasible for n ≤ 15-20 players.

        Returns:
            Dictionary mapping player to Shapley value
        """
        shapley_values = {player: 0.0 for player in self.players}

        # For each player i
        for i, player in enumerate(self.players):
            # For each coalition S not containing player i
            other_players = [p for p in self.players if p != player]

            # Iterate through all possible coalitions S ⊆ N \ {i}
            for size in range(len(other_players) + 1):
                for coalition_tuple in combinations(other_players, size):
                    coalition = set(coalition_tuple)

                    # Compute weight: |S|!(n-|S|-1)! / n!
                    s_size = len(coalition)
                    weight = (math.factorial(s_size) *
                             math.factorial(self.n - s_size - 1) /
                             math.factorial(self.n))

                    # Compute marginal contribution: v(S ∪ {i}) - v(S)
                    coalition_with_i = coalition | {player}
                    marginal = self._get_cost(coalition_with_i) - self._get_cost(coalition)

                    shapley_values[player] += weight * marginal

        return shapley_values

    def monte_carlo(self, num_samples: int = 1000, seed: int = None) -> Dict[str, float]:
        """
        Approximate Shapley values using Monte Carlo sampling.

        Algorithm:
            1. Generate random permutations of players
            2. For each permutation, compute marginal contribution when player joins
            3. Average over all samples

        Time Complexity: O(num_samples × n)
        Convergence: Error ∝ 1/√num_samples

        Args:
            num_samples: Number of random permutations to sample
            seed: Random seed for reproducibility

        Returns:
            Dictionary mapping player to approximate Shapley value
        """
        if seed is not None:
            np.random.seed(seed)

        marginal_contributions = defaultdict(list)

        for _ in range(num_samples):
            # Generate random permutation
            permutation = np.random.permutation(self.players).tolist()

            # Track coalition as we add players one by one
            coalition = set()

            for player in permutation:
                # Marginal contribution = cost(coalition ∪ {player}) - cost(coalition)
                coalition_with_player = coalition | {player}
                marginal = self._get_cost(coalition_with_player) - self._get_cost(coalition)

                marginal_contributions[player].append(marginal)

                # Add player to coalition
                coalition.add(player)

        # Average marginal contributions
        shapley_values = {
            player: np.mean(marginal_contributions[player])
            for player in self.players
        }

        return shapley_values

    def incremental(self, num_permutations: int = None, seed: int = None) -> Dict[str, float]:
        """
        Compute Shapley values using incremental algorithm.

        Similar to Monte Carlo but can enumerate all permutations for small n.

        Args:
            num_permutations: Number of permutations to sample (None = all permutations)
            seed: Random seed

        Returns:
            Dictionary mapping player to Shapley value
        """
        if num_permutations is None and self.n <= 10:
            # For small n, enumerate all n! permutations
            return self._incremental_exact()
        else:
            # For large n, sample permutations (equivalent to Monte Carlo)
            num_permutations = num_permutations or 1000
            return self.monte_carlo(num_permutations, seed)

    def _incremental_exact(self) -> Dict[str, float]:
        """Compute exact Shapley values by enumerating all permutations."""
        marginal_contributions = defaultdict(list)

        # Generate all n! permutations
        for permutation in permutations(self.players):
            coalition = set()

            for player in permutation:
                coalition_with_player = coalition | {player}
                marginal = self._get_cost(coalition_with_player) - self._get_cost(coalition)
                marginal_contributions[player].append(marginal)
                coalition.add(player)

        # Average over all permutations
        num_permutations = math.factorial(self.n)
        shapley_values = {
            player: sum(marginal_contributions[player]) / num_permutations
            for player in self.players
        }

        return shapley_values


class ShapleyAnalyzer:
    """
    Analyze properties of Shapley value allocation.

    Verifies:
        - Efficiency: Total Shapley values equal total cost
        - Individual rationality: No player pays more than standalone cost
        - Budget balance: Sum of allocations equals total cost
        - Core membership: Allocation is in the core (if applicable)
    """

    def __init__(self, players: List[str], cost_function: Callable[[Set[str]], float]):
        self.players = players
        self.cost_function = cost_function
        self.calculator = ShapleyValue(players, cost_function)

    def verify_efficiency(self, shapley_values: Dict[str, float], tolerance: float = 1e-6) -> bool:
        """
        Verify efficiency property: Σᵢφᵢ = v(N)

        Args:
            shapley_values: Computed Shapley values
            tolerance: Numerical tolerance

        Returns:
            True if efficiency property holds
        """
        total_shapley = sum(shapley_values.values())
        total_cost = self.cost_function(set(self.players))

        return abs(total_shapley - total_cost) < tolerance

    def verify_individual_rationality(self, shapley_values: Dict[str, float]) -> Dict[str, bool]:
        """
        Verify individual rationality: φᵢ ≤ c({i})

        Each player's allocation should not exceed their standalone cost.

        Args:
            shapley_values: Computed Shapley values

        Returns:
            Dictionary mapping player to whether IR is satisfied
        """
        ir_satisfied = {}

        for player in self.players:
            standalone_cost = self.cost_function({player})
            ir_satisfied[player] = shapley_values[player] <= standalone_cost

        return ir_satisfied

    def check_core_membership(self, shapley_values: Dict[str, float]) -> Tuple[bool, List[Set[str]]]:
        """
        Check if Shapley allocation is in the core.

        Core: Set of allocations where no coalition has incentive to deviate.
        Formally: For all S ⊆ N, Σᵢ∈S φᵢ ≤ c(S)

        Args:
            shapley_values: Computed Shapley values

        Returns:
            Tuple of (is_in_core, blocking_coalitions)
        """
        blocking_coalitions = []

        # Check all possible coalitions
        for size in range(1, len(self.players) + 1):
            for coalition_tuple in combinations(self.players, size):
                coalition = set(coalition_tuple)

                # Sum of Shapley values for coalition members
                coalition_shapley_sum = sum(shapley_values[p] for p in coalition)

                # Cost of coalition acting alone
                coalition_cost = self.cost_function(coalition)

                # If coalition pays more than standalone cost, it blocks
                if coalition_shapley_sum > coalition_cost + 1e-6:
                    blocking_coalitions.append(coalition)

        is_in_core = len(blocking_coalitions) == 0

        return is_in_core, blocking_coalitions

    def compute_savings(self, shapley_values: Dict[str, float]) -> Dict[str, float]:
        """
        Compute savings for each player compared to standalone cost.

        Savings = c({i}) - φᵢ

        Args:
            shapley_values: Computed Shapley values

        Returns:
            Dictionary mapping player to savings
        """
        savings = {}

        for player in self.players:
            standalone_cost = self.cost_function({player})
            savings[player] = standalone_cost - shapley_values[player]

        return savings

    def compute_cost_reduction_percentage(self, shapley_values: Dict[str, float]) -> Dict[str, float]:
        """
        Compute percentage cost reduction for each player.

        Reduction% = (c({i}) - φᵢ) / c({i}) × 100%

        Args:
            shapley_values: Computed Shapley values

        Returns:
            Dictionary mapping player to percentage reduction
        """
        reductions = {}

        for player in self.players:
            standalone_cost = self.cost_function({player})
            if standalone_cost > 0:
                reduction = (standalone_cost - shapley_values[player]) / standalone_cost * 100
                reductions[player] = reduction
            else:
                reductions[player] = 0.0

        return reductions


def compare_algorithms(players: List[str],
                       cost_function: Callable[[Set[str]], float],
                       num_samples: int = 1000) -> Dict[str, Dict[str, float]]:
    """
    Compare different Shapley value computation algorithms.

    Args:
        players: List of player identifiers
        cost_function: Cost function
        num_samples: Number of samples for Monte Carlo

    Returns:
        Dictionary with results from different algorithms
    """
    calculator = ShapleyValue(players, cost_function)

    results = {}

    # Exact algorithm (only for small n)
    if len(players) <= 12:
        results['exact'] = calculator.exact()

    # Monte Carlo
    results['monte_carlo'] = calculator.monte_carlo(num_samples=num_samples, seed=42)

    # Incremental
    if len(players) <= 10:
        results['incremental'] = calculator.incremental()
    else:
        results['incremental'] = calculator.incremental(num_permutations=num_samples, seed=42)

    return results


if __name__ == '__main__':
    # Example: Simple cost sharing game
    print("=" * 70)
    print("Shapley Value Calculation - Simple Example")
    print("=" * 70)

    # Define a simple cost function
    # Cost of serving customers with shared infrastructure
    def infrastructure_cost(coalition: Set[str]) -> float:
        """
        Cost function for shared infrastructure.

        Model: c(S) = fixed_cost + variable_cost × |S|
        Represents: Fixed infrastructure + per-customer maintenance
        """
        if len(coalition) == 0:
            return 0.0

        fixed_cost = 1000.0  # Infrastructure setup
        variable_cost = 100.0  # Per-customer maintenance

        return fixed_cost + variable_cost * len(coalition)

    # Three customers
    players = ['Customer_A', 'Customer_B', 'Customer_C']

    # Compute Shapley values
    calculator = ShapleyValue(players, infrastructure_cost)

    print("\n1. Exact Shapley Values:")
    exact_values = calculator.exact()
    for player, value in exact_values.items():
        print(f"   {player}: ${value:.2f}")

    print("\n2. Monte Carlo Approximation (1000 samples):")
    mc_values = calculator.monte_carlo(num_samples=1000, seed=42)
    for player, value in mc_values.items():
        error = abs(value - exact_values[player])
        print(f"   {player}: ${value:.2f} (error: ${error:.2f})")

    # Verify properties
    print("\n3. Property Verification:")
    analyzer = ShapleyAnalyzer(players, infrastructure_cost)

    is_efficient = analyzer.verify_efficiency(exact_values)
    print(f"   Efficiency: {is_efficient}")
    print(f"   Total cost: ${sum(exact_values.values()):.2f}")
    print(f"   Coalition cost: ${infrastructure_cost(set(players)):.2f}")

    ir = analyzer.verify_individual_rationality(exact_values)
    print(f"\n   Individual Rationality:")
    for player, satisfied in ir.items():
        standalone = infrastructure_cost({player})
        print(f"   {player}: {satisfied} (Shapley: ${exact_values[player]:.2f}, Standalone: ${standalone:.2f})")

    is_in_core, blocking = analyzer.check_core_membership(exact_values)
    print(f"\n   Core membership: {is_in_core}")
    if not is_in_core:
        print(f"   Blocking coalitions: {blocking}")

    savings = analyzer.compute_savings(exact_values)
    print(f"\n   Savings compared to standalone:")
    for player, saving in savings.items():
        reduction_pct = analyzer.compute_cost_reduction_percentage(exact_values)[player]
        print(f"   {player}: ${saving:.2f} ({reduction_pct:.1f}% reduction)")

    print("\n" + "=" * 70)
