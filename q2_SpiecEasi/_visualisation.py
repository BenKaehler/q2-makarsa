import tempfile
import json
import pkg_resources
from collections import defaultdict
from pathlib import Path

import networkx as nx
import pandas as pd

import q2templates

TEMPLATES = Path(pkg_resources.resource_filename('q2_SpiecEasi', 'assets'))

EXTENDS = "{% extends 'tabbed.html' %}\n"

TITLE = '{% block title %}q2-SpiecEasi : {{ title }}{% endblock %}\n'

HEAD = '''
{% block head %}
<script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
<link rel="stylesheet" href="./assets/css/vega.css">
{% endblock %}
'''

TABCONTENT = """
{% block tabcontent %}
  <div id="view"></div>
  <script type="text/javascript">
    var spec = {{ spec }};
    var view;

    render(spec).catch(err => console.error(err));

    function render(spec) {
      view = new vega.View(vega.parse(spec), {
        renderer:  'svg',  // renderer (canvas or svg)
        container: '#view',   // parent DOM container
        hover:     true       // enable hover processing
      });
      return view.runAsync();
    }
  </script>
{% endblock %}
"""

TABLECONTENT = """
{% block tabcontent %}
{{ table }}
{% endblock %}
"""


def graph_to_spec(network):
    with open(TEMPLATES / 'force-directed-layout.vg.json') as fh:
        spec = json.load(fh)
    nodes = nx.nodes(network)
    idx = {nid: i for i, nid in enumerate(nodes)}
    nodes = [{'index': idx[nid], **nodes[nid]} for nid in nodes]
    edges = nx.edges(network)
    links = [{'source': idx[n[0]], 'target': idx[n[1]], **edges[n]}
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
    return spec


def get_connected_components(network):
    network = nx.to_undirected(network)
    groups = defaultdict(list)
    pairs = []
    singles = []
    components = [network.subgraph(c).copy()
                  for c in nx.connected_components(network)]
    for subgraph in components:
        order = subgraph.order()
        if order == 1:
            for nid, attr in subgraph.nodes(data=True):
                singles.append(attr['name'])
        elif order == 2:
            pair = [a['name'] for _, a in subgraph.nodes(data=True)]
            pairs.append(pair)
        else:
            groups[order].append(subgraph)
    orders = list(groups.keys())
    orders.sort(reverse=True)
    groups = [g for o in orders for g in groups[o]]
    return groups, pairs, singles


def create_html_file(directory, source_file, title, content):
    tab = {'url': source_file, 'title': title}
    path = directory / source_file
    with open(path, 'w') as fh:
        fh.write(content)
    return path, tab


def visualise_network(
        output_dir: str,
        network: nx.Graph) -> None:

    q2templates.util.copy_assets(TEMPLATES / 'assets', Path(output_dir) / 'assets')

    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)

        groups, pairs, singles = get_connected_components(network)

        source_files = []
        tabs = []
        for i, graph in enumerate(groups):
            if i == 0:
                source_file = 'index.html'
                content = EXTENDS + TITLE + HEAD
            else:
                source_file = f'group-{i+1}.html'
                content = EXTENDS + HEAD
            title = f'Group {i+1}'
            spec = json.dumps(graph_to_spec(graph), indent=1)
            content += TABCONTENT.replace('{{ spec }}', spec)

            source_file, tab = create_html_file(
                    temp_dir, source_file, title, content)
            tabs.append(tab)
            source_files.append(source_file)

        if pairs:
            pairs_table = pd.DataFrame(
                pairs, columns=['Feature 1', 'Feature 2'])
            table = q2templates.df_to_html(pairs_table, index=False)
            content = EXTENDS + TABLECONTENT.replace('{{ table }}', table)
            source_file, tab = create_html_file(
                    temp_dir, 'pairs.html', 'Pairs', content)
            tabs.append(tab)
            source_files.append(source_file)

        if singles:
            singles_table = pd.DataFrame(singles, columns=['Feature'])
            table = q2templates.df_to_html(singles_table, index=False)
            content = EXTENDS + TABLECONTENT.replace('{{ table }}', table)
            source_file, tab = create_html_file(
                    temp_dir, 'singles.html', 'Singles', content)
            tabs.append(tab)
            source_files.append(source_file)

        q2templates.render(source_files, output_dir,
                           context={'title': 'Networks', 'tabs': tabs})
