import numpy as np
import itertools
from scipy.optimize import linprog

def find_nash_equilibrium_three_player(payoff_matrices):
    """
    Attempts to find a Nash equilibrium for a three-player zero-sum game.
    Uses an extended version of Nash computation by checking for best responses.
    
    Parameters:
    payoff_matrices (tuple of np.array): Three payoff matrices for three players
    
    Returns:
    list: List of strategy profiles that are Nash equilibria
    """
    A, B, C = payoff_matrices
    num_strategies = A.shape[0]
    equilibria = []
    
    for strategies in itertools.product(range(num_strategies), repeat=3):
        i, j, k = strategies
        
        # Best response check for Player 1
        if A[i, j, k] < max(A[:, j, k]):
            continue
        
        # Best response check for Player 2
        if B[i, j, k] < max(B[i, :, k]):
            continue
        
        # Best response check for Player 3
        if C[i, j, k] < max(C[i, j, :]):
            continue
        
        equilibria.append(strategies)
    
    return equilibria

# Example payoff matrices for a 3x3x3 three-player zero-sum game
A = np.random.randint(-5, 5, (3, 3, 3))
B = np.random.randint(-5, 5, (3, 3, 3))
C = -(A + B)  # Ensure zero-sum condition

# Compute Nash equilibria
nash_equilibria = find_nash_equilibrium_three_player((A, B, C))

print("Nash Equilibria:")
for eq in nash_equilibria:
    print(eq)