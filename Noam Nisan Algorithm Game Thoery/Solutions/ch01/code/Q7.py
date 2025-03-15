import numpy as np
import sympy as sp

def total_income_monopoly(demand_function, q_symbol):
    """
    Computes the total income for a monopolist given a demand function.

    Parameters:
    demand_function (sympy expression): Demand-price function p(q)
    q_symbol (sympy.Symbol): Symbol representing quantity q

    Returns:
    float: Revenue R_m for monopolist
    """
    revenue = q_symbol * demand_function
    optimal_q = sp.solve(sp.diff(revenue, q_symbol), q_symbol)
    if optimal_q:
        q_m = max(optimal_q)  # Choose the valid root
        return revenue.subs(q_symbol, q_m).evalf()
    return None

def total_income_competition(demand_function, q_symbol, n_firms):
    """
    Computes the total income for an n-firm competitive market.

    Parameters:
    demand_function (sympy expression): Demand-price function p(q)
    q_symbol (sympy.Symbol): Symbol representing quantity q
    n_firms (int): Number of competing firms

    Returns:
    float: Total revenue in competitive setting
    """
    q_i = sp.Symbol("q_i")
    total_q = n_firms * q_i
    revenue_per_firm = q_i * demand_function.subs(q_symbol, total_q)
    optimal_q_i = sp.solve(sp.diff(revenue_per_firm, q_i), q_i)
    
    if optimal_q_i:
        q_c = max(optimal_q_i)  # Choose the valid root
        return n_firms * revenue_per_firm.subs(q_i, q_c).evalf()
    return None

def analyze_bertrand_game(p_function, n_firms):
    """
    Analyzes the Bertrand game for both monopoly and competition.

    Parameters:
    p_function (str): Demand-price function as a string, e.g., "1 - q"
    n_firms (int): Number of competing firms

    Returns:
    dict: Monopolist and competition total revenues
    """
    q = sp.Symbol("q")
    demand_function = sp.sympify(p_function)

    monopoly_income = total_income_monopoly(demand_function, q)
    competition_income = total_income_competition(demand_function, q, n_firms)

    return {
        "Monopoly Income": monopoly_income,
        "Competition Income": competition_income,
        "Monopoly vs. Competition Ratio": monopoly_income / competition_income if competition_income else None
    }

def get_user_input():
    """
    Allows the user to input a custom demand function and number of firms.

    Returns:
    tuple: Demand function as a string and number of firms
    """
    p_function = input("Enter the demand-price function p(q), e.g., '1 - q': ")
    n_firms = int(input("Enter the number of firms competing: "))
    return p_function, n_firms

# Predefined test cases
print("\nRunning predefined test cases...")
test_cases = [
    ("1 - q", 2),
    ("2 - 0.5*q", 3)
]

# Run predefined test cases
for i, (p_func, n) in enumerate(test_cases, 1):
    print(f"\nTest Case {i}:")
    result = analyze_bertrand_game(p_func, n)
    print("Analysis Result:", result)

# Allow user input for custom cases
print("\n--- User-defined Test Case ---")
user_p_func, user_n_firms = get_user_input()
user_result = analyze_bertrand_game(user_p_func, user_n_firms)
print("User-defined Test Case - Analysis Result:", user_result)
