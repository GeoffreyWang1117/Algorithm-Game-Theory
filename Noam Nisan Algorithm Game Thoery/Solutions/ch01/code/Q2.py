import numpy as np
import nashpy as nash
import warnings

# Suppress runtime warnings from Nashpy
warnings.filterwarnings("ignore", category=RuntimeWarning)

def has_pure_nash_equilibrium(A, B):
    """
    Checks if a given two-player game has a pure Nash equilibrium manually
    without relying solely on support enumeration.

    Parameters:
    A (np.array): Payoff matrix for Player 1
    B (np.array): Payoff matrix for Player 2

    Returns:
    bool: True if there exists at least one pure Nash equilibrium, False otherwise
    """
    num_strategies = A.shape[0]

    for i in range(num_strategies):
        for j in range(num_strategies):
            # Check if player 1 has the best response at (i, j)
            if A[i, j] >= np.max(A[:, j]) and B[i, j] >= np.max(B[i, :]):
                return True  # Found a pure Nash equilibrium
    return False

def estimate_pure_nash_probability(n, trials=10000):
    """
    Estimates the probability of a pure Nash equilibrium existing in an n x n random game.

    Parameters:
    n (int): Number of strategies per player
    trials (int): Number of random games to simulate

    Returns:
    float: Estimated probability of a pure Nash equilibrium existing
    """
    count = 0
    for _ in range(trials):
        A = np.random.rand(n, n)
        B = np.random.rand(n, n)
        if has_pure_nash_equilibrium(A, B):
            count += 1
    return count / trials

# Running the probability estimation for different values of n
for n in [2, 3, 5, 10]:
    probability = estimate_pure_nash_probability(n, trials=1000)
    print(f"Estimated probability of pure Nash equilibrium for {n}x{n} game: {probability:.4f}")