import networkx as nx

def find_pure_nash_tree(graph, payoffs):
    """
    Determines if a pure Nash equilibrium exists in a 2-strategy n-player tree game.

    Parameters:
    graph (nx.Graph): A tree graph where nodes are players.
    payoffs (dict): A dictionary where payoffs[(player, strategy)] gives the player's payoff.

    Returns:
    bool: True if a pure Nash equilibrium exists, False otherwise.
    """

    def dfs(node, parent, chosen_strategy):
        """
        Tree DP to check if the current node's chosen strategy is stable given its neighbors.
        """
        for neighbor in graph.neighbors(node):
            if neighbor == parent:  # Avoid revisiting parent in tree
                continue

            # Try both strategies (0 and 1) for neighbor
            valid = False
            for neighbor_strategy in [0, 1]:
                # Check if choosing this strategy ensures a stable equilibrium
                if payoffs[(neighbor, neighbor_strategy)] >= payoffs[(neighbor, 1 - neighbor_strategy)]:
                    if dfs(neighbor, node, neighbor_strategy):
                        valid = True
                        break

            if not valid:
                return False
        return True

    root = list(graph.nodes())[0]  # Start from an arbitrary node
    return dfs(root, None, 0) or dfs(root, None, 1)  # Try both strategies for root

def get_user_input_tree():
    """
    Allows the user to input a custom tree structure and payoff values.

    Expected input format:
    - Enter the number of nodes in the tree (n).
    - Enter edges connecting nodes in the format "node1 node2".
      Example:
        0 1
        1 2
        1 3
      Type "done" when finished.
    - Enter payoffs in the format "node strategy payoff".
      Example:
        0 0 3
        0 1 4
        1 0 2
        1 1 5
      Type "done" when finished.
    
    Returns:
    graph (nx.Graph): The input tree graph.
    payoffs (dict): The input payoff values.
    """
    G = nx.Graph()
    n = int(input("Enter number of nodes in the tree: "))

    print("\nEnter tree edges in the format 'node1 node2'. Type 'done' to finish.")
    print("Example:\n  0 1\n  1 2\n  1 3\n  done")
    while True:
        edge = input()
        if edge.lower() == 'done':
            break
        u, v = map(int, edge.split())
        G.add_edge(u, v)
    
    payoffs = {}
    print("\nEnter payoffs in the format 'node strategy payoff'. Type 'done' to finish.")
    print("Example:\n  0 0 3\n  0 1 4\n  1 0 2\n  1 1 5\n  done")
    while True:
        data = input()
        if data.lower() == 'done':
            break
        node, strategy, payoff = map(int, data.split())
        payoffs[(node, strategy)] = payoff
    
    return G, payoffs

# Inform user about predefined test cases
print("\nRunning predefined test cases...")
test_cases = [
    {
        "graph": nx.Graph([(0, 1), (1, 2), (1, 3)]),
        "payoffs": {
            (0, 0): 3, (0, 1): 4,
            (1, 0): 2, (1, 1): 5,
            (2, 0): 1, (2, 1): 3,
            (3, 0): 2, (3, 1): 4,
        }
    },
    {
        "graph": nx.Graph([(0, 1), (1, 2)]),
        "payoffs": {
            (0, 0): 1, (0, 1): 2,
            (1, 0): 2, (1, 1): 3,
            (2, 0): 3, (2, 1): 1,
        }
    }
]

# Run predefined test cases
for i, test in enumerate(test_cases, 1):
    print(f"\nTest Case {i}:")
    result = find_pure_nash_tree(test["graph"], test["payoffs"])
    print(f"Has Pure Nash Equilibrium: {result}")

# Allow user input for custom cases
print("\n--- User-defined Test Case ---")
G_user, payoffs_user = get_user_input_tree()
result_user = find_pure_nash_tree(G_user, payoffs_user)
print(f"User-defined Test Case - Has Pure Nash Equilibrium: {result_user}")