from typing import List, Optional, Set, Union

import networkx as nx


def find_cycle(G: nx.Graph, **kwargs: dict) -> List:
    """Wraps networkx.find_cycle to return empty list
    if no cycle is found.
    """
    try:
        return list(nx.find_cycle(G, **kwargs))

    except nx.exception.NetworkXNoCycle:
        return []


def get_subset(g: nx.DiGraph, nodes: Union[str, Set[str], List[str]]) -> Set[str]:
    """This algorithm is for determining which nodes in a graph must be re-solved if
    `nodes` are dirty. It looks for the immediate parents of each dirty node, all
    descendants of the dirty nodes down to the root node (no 'out' edge connections),
    and the immediate parents of _each_ descdendant. This algorithm only works on
    directed acyclic graphs (DAGs).
    """
    if isinstance(nodes, (int, str)):
        nodes = [nodes]

    node_parents = {s for n in nodes for s in g.predecessors(n)}
    desc = {s for n in nodes for s in get_all_successors(g, n)}
    desc_parents = {s for d in desc for s in g.predecessors(d)}

    return set(nodes) | node_parents | desc | desc_parents


def get_all_predecessors(
    g: nx.DiGraph, node: str, subset: Optional[Set[str]] = None
) -> Set[str]:
    """This algorithm is a good deal faster than the nx.ancestors variant,
    **but** it only works on directed acyclic graphs (DAGs).
    """
    if subset is None:
        subset = set()

    for p in g.predecessors(node):
        subset.add(p)
        get_all_predecessors(g, p, subset=subset)
    return subset


def get_all_successors(
    g: nx.DiGraph, node: str, subset: Optional[Set[str]] = None
) -> Set[str]:
    """This algorithm is a good deal faster than the nx.descendants variant,
    **but** it only works on directed acyclic graphs (DAGs).
    """
    if subset is None:
        subset = set()

    for s in g.successors(node):
        subset.add(s)
        get_all_successors(g, s, subset=subset)
    return subset


def find_leafy_branch_larger_than_size(G: nx.DiGraph, size: int = 1) -> nx.DiGraph:
    """This algorithm will sort the graph `G` and return the outermost
    contiguous subgraph that is larger than `size`
    """
    if not nx.is_weakly_connected(G):
        raise nx.NetworkXUnfeasible("Graphs must be directed and weakly connected.")

    # exit early if our graph is already the right size
    if len(G) <= size:
        return G

    # Start at the leaves and work through branches.
    # Return first subgraph larger than or equal to `size`.
    for node in nx.lexicographical_topological_sort(G):  # pragma: no branch
        us = get_all_predecessors(G, node)
        us.add(node)
        if len(us) >= size:
            return G.subgraph(us)


def sequential_subgraph_nodes(G: nx.DiGraph, size: int) -> List[List[Union[str, int]]]:

    if not nx.is_weakly_connected(G):
        raise nx.NetworkXUnfeasible(
            "sequential solutions are not possible for disconnected graphs."
        )

    if size <= 1:
        raise nx.NetworkXUnfeasible("the minimum directed subgraph length is 2 nodes.")

    g = G.copy()  # make a copy because we'll modify the structure

    graphs = []

    while len(g.nodes()) > 1:

        sg = find_leafy_branch_larger_than_size(g, size)

        sg_nodes = list(nx.lexicographical_topological_sort(sg))
        graphs.append(sg_nodes)

        # trim the upstream nodes out of the graph, except the upstream root
        us_nodes = [n for n, deg in sg.out_degree if deg > 0]
        g = g.subgraph([n for n in g.nodes() if n not in us_nodes])

        # rinse and repeat until there's one or fewer nodes left in the graph

    return graphs


def parallel_sequential_subgraph_nodes(
    G: nx.DiGraph, size: int
) -> List[List[List[Union[str, int]]]]:
    # strip the input graph to just the edge info
    g = nx.DiGraph()
    g.add_edges_from(G.edges())

    parallel_graphs = []

    # Weakly connected components are to directed graphs as
    # connected components are to undirected graphs.
    # In this case, it separates the input graph into subgraphs
    # with different root nodes, or outfalls.
    for ws in nx.weakly_connected_components(g):

        ws_graph = g.subgraph(ws)

        sequential_subgraphs = sequential_subgraph_nodes(ws_graph, size)

        parallel_graphs.append(sequential_subgraphs)

    return parallel_graphs
