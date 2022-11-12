import json
from pathlib import Path
import pkg_resources

import networkx as nx

import q2templates

TEMPLATES = Path(pkg_resources.resource_filename('q2_SpiecEasi', 'assets'))


def visualise_network(
        output_dir: str,
        network: nx.Graph) -> None:
    title = 'SpiecEasi Network'
    index = TEMPLATES / 'index.html'
    with open(TEMPLATES / 'force-directed-layout.vg.json') as fh:
        spec = json.load(fh)
    nodes = nx.nodes(network)
    nodes = [{'index': int(nid[1:]), **nodes[nid]} for nid in nodes]
    edges = nx.edges(network)
    links = [{'source': int(n[0][1:]), 'target': int(n[1][1:]), **edges[n]}
             for n in edges]
    # "group" in nodes is currently being used for colour
    # "value" in links has been dropped. not sure whether it did anything
    spec["data"] = [
        {
          "name": "node-data",
          "values": nodes
        },
        {
          "name": "link-data",
          "values": links
        }]

    q2templates.render([index], output_dir, context={
        'title': title, 'spec': json.dumps(spec, indent=1)})
