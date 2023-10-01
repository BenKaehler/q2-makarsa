# Everybody needs good neighbours.

from networkx import Graph
from pandas import DataFrame
from qiime2 import Metadata

from ._visualisation import annotate_node_stats, annotate_with_metadata


def list_neighbours(
        network: Graph,
        feature_id: str,
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

    # Find the neighbours of the feature node
    neighbours = list(network.neighbors(feature_node))

    # Create a table of the neighbours, where the index is
    # the feature ID, and the columns are the node attributes.
    result = DataFrame(
        [dict(network.nodes[x]) for x in neighbours],
        index=neighbours)
    result.index = result["Feature"]
    result = result.drop(columns=["Feature"])
    result.index.name = "Feature ID"
    for column in result.columns:
        if column.startswith("Taxon Level "):
            result = result.drop(columns=[column])

    # Add a column to result for the edge weight between
    # the feature and each neighbour.
    result[f"Weight to {feature_id}"] = [
        network.edges[feature_node, x]["weight"] for x in neighbours]

    return Metadata(result)
