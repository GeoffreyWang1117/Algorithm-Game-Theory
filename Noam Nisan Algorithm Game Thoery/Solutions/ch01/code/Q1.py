import numpy as np
import nashpy as nash

def solve_nash_equilibrium(matrix1, matrix2):
    """
    Solve the Nash equilibrium for a two-player game using different methods.
    
    Parameters:
    matrix1 (np.array): Payoff matrix for player 1
    matrix2 (np.array): Payoff matrix for player 2
    
    Returns:
    dict: A dictionary containing Nash equilibria found using different methods.
    """
    # Validate input matrices
    if matrix1.shape != matrix2.shape:
        raise ValueError("The payoff matrices must have the same dimensions.")
    
    game = nash.Game(matrix1, matrix2)
    
    # Solve using support enumeration
    support_equilibria = list(game.support_enumeration())
    
    # Solve using vertex enumeration
    vertex_equilibria = list(game.vertex_enumeration())
    
    return {
        "Support Enumeration": support_equilibria,
        "Vertex Enumeration": vertex_equilibria
    }

def get_user_input_matrix():
    """
    Get a user-defined payoff matrix.
    Returns:
    np.array: User-defined matrix.
    """
    n = int(input("Enter the number of strategies for each player: "))
    print("Enter the payoff matrix row-wise for Player 1:")
    matrix1 = np.array([list(map(float, input().split())) for _ in range(n)])
    
    print("Enter the payoff matrix row-wise for Player 2:")
    matrix2 = np.array([list(map(float, input().split())) for _ in range(n)])

    return matrix1, matrix2

# Predefined test cases
test_cases = [
    (np.array([[3, 0], [5, 1]]), np.array([[3, 5], [0, 1]])),
    (np.array([[2, -1], [0, 3]]), np.array([[-2, 1], [0, -3]])),
    (np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), np.array([[9, 8, 7], [6, 5, 4], [3, 2, 1]]))
]

# Run predefined test cases
for i, (A, B) in enumerate(test_cases, 1):
    print(f"\nTest Case {i}:")
    equilibria = solve_nash_equilibrium(A, B)
    print("Nash Equilibria found:")
    for method, eqs in equilibria.items():
        print(f"\nMethod: {method}")
        for eq in eqs:
            print(f"  {eq}")

# Allow user input for custom payoff matrices
print("\n--- User-defined Game ---")
A_user, B_user = get_user_input_matrix()
equilibria_user = solve_nash_equilibrium(A_user, B_user)

print("Nash Equilibria found:")
for method, eqs in equilibria_user.items():
    print(f"\nMethod: {method}")
    for eq in eqs:
        print(f"  {eq}")
