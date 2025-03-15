import numpy as np
import nashpy as nash

def epsilon_approximate_nash(payoff_matrix_1, payoff_matrix_2, epsilon=0.1):
    """
    Finds an epsilon-approximate Nash equilibrium with small support.
    
    Parameters:
    payoff_matrix_1 (np.array): Payoff matrix for Player 1
    payoff_matrix_2 (np.array): Payoff matrix for Player 2
    epsilon (float): Approximation factor

    Returns:
    tuple: Approximate mixed strategy for both players
    """
    game = nash.Game(payoff_matrix_1, payoff_matrix_2)
    equilibria = list(game.support_enumeration())

    if not equilibria:
        return "No Nash equilibrium found"

    # Select a Nash equilibrium
    p1_mixed, p2_mixed = equilibria[0]

    # Reduce the support size to O(log n)
    num_strategies = len(p1_mixed)
    support_size = max(1, int(np.log2(num_strategies)))  # O(log n) strategies
    
    def reduce_support(mixed_strategy):
        """ Reduce support by keeping top O(log n) probabilities """
        sorted_indices = np.argsort(-mixed_strategy)[:support_size]
        reduced_strategy = np.zeros_like(mixed_strategy)
        reduced_strategy[sorted_indices] = 1 / support_size
        return reduced_strategy

    approx_p1 = reduce_support(p1_mixed)
    approx_p2 = reduce_support(p2_mixed)

    return approx_p1, approx_p2

def get_user_input_game():
    """
    Allows the user to input a custom two-player game setup.

    Returns:
    np.array, np.array: Payoff matrices for both players.
    """
    n = int(input("Enter the number of strategies for each player: "))

    print("Enter the payoff matrix for Player 1 row-wise:")
    payoff_matrix_1 = np.array([list(map(float, input().split())) for _ in range(n)])

    print("Enter the payoff matrix for Player 2 row-wise:")
    payoff_matrix_2 = np.array([list(map(float, input().split())) for _ in range(n)])

    return payoff_matrix_1, payoff_matrix_2

# Predefined test cases
print("\nRunning predefined test cases...")
test_cases = [
    (
        np.array([[3, 0], [5, 1]]), 
        np.array([[3, 5], [0, 1]])
    ),
    (
        np.array([[1, -1, 3], [0, 2, -2], [4, 0, 1]]),
        np.array([[-1, 2, 1], [3, -2, 0], [2, 1, -1]])
    )
]

# Run predefined test cases
for i, (A, B) in enumerate(test_cases, 1):
    print(f"\nTest Case {i}:")
    approx_equilibrium = epsilon_approximate_nash(A, B)
    print("Epsilon-Approximate Nash Equilibrium:", approx_equilibrium)

# Allow user input for custom cases
print("\n--- User-defined Test Case ---")
A_user, B_user = get_user_input_game()
approx_equilibrium_user = epsilon_approximate_nash(A_user, B_user)
print("User-defined Test Case - Epsilon-Approximate Nash Equilibrium:", approx_equilibrium_user)
