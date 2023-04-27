from collections import deque

import networkx as nx
from statemachine import StateMachine


def ordered_nodes_by_distance(graph, start_node):
    visited = set()  # Set to store visited nodes
    distance_ordered_nodes = []  # List to store nodes in increasing distance order

    queue = deque([start_node])  # Queue to store nodes to be visited

    while queue:
        current_node = queue.popleft()
        if current_node not in visited:
            visited.add(current_node)
            distance_ordered_nodes.append(current_node)

            # Enqueue the neighbors of the current node
            for neighbor in graph.neighbors(current_node):
                if neighbor not in visited:
                    queue.append(neighbor)

    return distance_ordered_nodes


def get_graph(machine: StateMachine) -> nx.DiGraph:
    graph = nx.DiGraph()
    # graph.add_node(machine._initial_node())
    # graph.add_edge(machine._initial_edge())

    for state in machine.states:
        node_data = {
            k: v
            for k, v in state.__dict__.items()
            if isinstance(v, (str, int, float, bool))
        }
        graph.add_node(state.id, **node_data)
        for transition in state.transitions:
            if transition.internal:
                continue
            edge_data = {
                k: v
                for k, v in transition.__dict__.items()
                if isinstance(v, (str, int, float, bool))
            }
            graph.add_edge(transition.source.id, transition.target.id, **edge_data)

    return graph
