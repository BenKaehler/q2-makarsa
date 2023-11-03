# Everybody needs good neighbours.

from networkx import Graph, shortest_path_length
from pandas import DataFrame
from qiime2 import Metadata

from ._visualisation import annotate_node_stats, annotate_with_metadata


def list_neighbours(
        network: Graph,
        feature_id: str,
        radius: int = 1,
        metadata: Metadata = None) -> Metadata:
    """List the neighbours of a feature in a network.

    Parameters
    ----------
    network : Graph
        The network to search.
    feature_id : str
        The feature for which to list neighbours.
    metadata : Metadata, optional
        Any additional metadata to include in the output.

    Returns
    -------
    DataFrame
        The neighbours of the feature, with metadata.
    """
    if metadata:
        annotate_with_metadata(network, metadata)
    annotate_node_stats(network)

    # Find the node for which the "Feature" attribute is feature_id
    feature_node = [
        x for x in network.nodes
        if network.nodes[x]["Feature"] == feature_id]
    if not feature_node:
        raise ValueError(f"Feature {feature_id} not found in network")
    feature_node = feature_node[0]

    # Find the nodes within the given radius
    nodes_within_radius = [
        (node, path_length) for node, path_length in
        shortest_path_length(network, source=feature_node).items()
        if 0 < path_length <= radius]

    # Create a table of the neighbours, where the index is
    # the feature ID, and the columns are the node attributes.
    result = DataFrame(
        [dict(network.nodes[node],
              **{f"Weight to {feature_id}":
                 network.edges[feature_node, node]["weight"]
                 if path_length == 1 else float("nan"),
                 f"Path Length to {feature_id}": path_length})
         for node, path_length in nodes_within_radius],
        index=list(zip(*nodes_within_radius))[0])
    result.index = result["Feature"]
    result = result.drop(columns=["Feature"])
    result.index.name = "Feature ID"
    for column in result.columns:
        if column.startswith("Taxon Level "):
            result = result.drop(columns=[column])

    return Metadata(result)
