

from scipy.optimize import linprog
import numpy as np

def find_correlated_equilibrium(n, u_on, u_off):
    """
    Finds a correlated equilibrium for an n-player symmetric game with "on" and "off" strategies.
    
    Parameters:
    n (int): Number of players.
    u_on (list): List of payoffs when choosing "on" given k other players chose "on".
    u_off (list): List of payoffs when choosing "off" given k other players chose "on".
    
    Returns:
    dict: Probability distribution over strategy profiles.
    """
    # Number of strategy profiles (each player can be "on" or "off")
    num_profiles = 2 ** n

    # Construct probability variables (one for each profile)
    P = np.ones(num_profiles) / num_profiles  # Initialize uniform distribution

    # Constraints: Each player must not benefit from deviation
    constraints = []
    b = []

    for k in range(n):  # Number of other players choosing "on"
        # Expected utility constraints
        constraints.append([1 if bin(i).count("1") == k else 0 for i in range(num_profiles)])
        b.append(u_on[k] - u_off[k])

    # Solve LP: Find valid P satisfying all constraints
    res = linprog(c=np.zeros(num_profiles), A_eq=[np.ones(num_profiles)], b_eq=[1], A_ub=constraints, b_ub=b, method='highs')

    if res.success:
        return {bin(i)[2:].zfill(n): round(p, 3) for i, p in enumerate(res.x)}
    else:
        return "No correlated equilibrium found."

def get_user_input_game():
    """
    Allows the user to input a custom n-player game setup.
    
    Expected input format:
    - Enter the number of players (n).
    - Enter payoffs for choosing "on" when k players (excluding oneself) also choose "on."
      Example (for n=4): 3 4 5 6
    - Enter payoffs for choosing "off" when k players (excluding oneself) also choose "on."
      Example (for n=4): 2 3 4 5
    
    Returns:
    n (int): Number of players.
    u_on (list): Payoffs for choosing "on."
    u_off (list): Payoffs for choosing "off."
    """
    n = int(input("Enter the number of players: "))
    
    print("\nEnter payoffs for choosing 'on' when k players (excluding oneself) also choose 'on'.")
    print(f"Example (for {n} players): 3 4 5 ... {n+2}")
    u_on = list(map(int, input().split()))

    print("\nEnter payoffs for choosing 'off' when k players (excluding oneself) also choose 'on'.")
    print(f"Example (for {n} players): 2 3 4 ... {n+1}")
    u_off = list(map(int, input().split()))

    return n, u_on, u_off

# Predefined test cases
print("\nRunning predefined test cases...")
test_cases = [
    (4, [3, 4, 5, 6], [2, 3, 4, 5]),
    (3, [2, 3, 4], [1, 2, 3])
]

# Run predefined test cases
for i, (n, u_on, u_off) in enumerate(test_cases, 1):
    print(f"\nTest Case {i}:")
    result = find_correlated_equilibrium(n, u_on, u_off)
    print("Correlated Equilibrium Distribution:", result)

# Allow user input for custom cases
print("\n--- User-defined Test Case ---")
n_user, u_on_user, u_off_user = get_user_input_game()
result_user = find_correlated_equilibrium(n_user, u_on_user, u_off_user)
print("User-defined Test Case - Correlated Equilibrium Distribution:", result_user)