import networkx as nx

def compute_mst_cost_sharing(graph):
    """
    Computes the minimum spanning tree (MST) and assigns cost-sharing among agents.

    Parameters:
    graph (nx.Graph): A complete graph with weighted edges.

    Returns:
    dict: Cost allocation for each agent.
    """
    # Compute MST using Kruskal's algorithm
    mst = nx.minimum_spanning_tree(graph, algorithm='kruskal')

    # Assign cost to each agent based on their first connection in the MST
    cost_allocation = {}
    for edge in mst.edges(data=True):
        node1, node2, cost = edge[0], edge[1], edge[2]['weight']
        if node1 == 0:
            cost_allocation[node2] = cost
        elif node2 == 0:
            cost_allocation[node1] = cost

    return cost_allocation, mst

def get_user_input_graph():
    """
    Allows the user to input a custom weighted graph.

    Returns:
    nx.Graph: The input graph.
    """
    G = nx.Graph()
    n = int(input("Enter number of agents (excluding root node 0): ")) + 1

    print("Enter edges in the format 'node1 node2 cost'. Type 'done' to finish.")
    print("Example:\n  0 1 3\n  0 2 2\n  1 2 1\n  done")
    while True:
        edge = input()
        if edge.lower() == 'done':
            break
        u, v, cost = map(int, edge.split())
        G.add_edge(u, v, weight=cost)

    return G

# Predefined test cases
print("\nRunning predefined test cases...")
test_cases = [
    nx.Graph([(0, 1, {'weight': 3}), (0, 2, {'weight': 2}), (1, 2, {'weight': 1})]),
    nx.Graph([(0, 1, {'weight': 4}), (0, 2, {'weight': 5}), (1, 2, {'weight': 2}), (2, 3, {'weight': 3})])
]

# Run predefined test cases
for i, test_graph in enumerate(test_cases, 1):
    print(f"\nTest Case {i}:")
    cost_allocation, mst = compute_mst_cost_sharing(test_graph)
    print("Cost Allocation:", cost_allocation)
    print("Minimum Spanning Tree Edges:", list(mst.edges(data=True)))

# Allow user input for custom cases
print("\n--- User-defined Test Case ---")
user_graph = get_user_input_graph()
user_cost_allocation, user_mst = compute_mst_cost_sharing(user_graph)
print("User-defined Test Case - Cost Allocation:", user_cost_allocation)
print("User-defined Test Case - Minimum Spanning Tree Edges:", list(user_mst.edges(data=True)))
