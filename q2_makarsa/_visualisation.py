import json
import tempfile
from collections import defaultdict
from pathlib import Path
import pkg_resources

import networkx as nx
import pandas as pd
import numpy as np
import q2templates
import qiime2

TEMPLATES = Path(pkg_resources.resource_filename("q2_makarsa", "assets"))

TABBUTTON = """
<button class="tablinks" onclick="openTab(event, '{{ tabtitle }}')">
{{ tabtitle }}</button>
"""

INDEX = """
{% extends 'base.html' %}

{% block title %}q2-makarsa : {{ title }}{% endblock %}

{% block head %}
<script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
<link rel="stylesheet" href="./assets/css/vega.css">
<link rel="stylesheet" href="./assets/css/tabs.css">
{% endblock %}

{% block content %}
<!-- Tab links -->
<div class="tab">
{{ tabbuttons }}
</div>

<!-- Tab content -->
{{ tabcontents }}

<script type="text/javascript">
var lastSuffix;

function openTab(evt, tabName) {
  // thanks https://www.w3schools.com/howto/howto_js_tabs.asp

  // Declare all variables
  var i, tabcontent, tablinks;

  // Get all elements with class="tabcontent" and hide them
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }

  // Get all elements with class="tablinks" and remove the class "active"
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }

  // Show the current tab, and add an "active" class to the
  // button that opened the tab
  var splitTabName = tabName.split(" ");
  if (splitTabName.length > 1)
  {
    var thisSuffix = splitTabName.pop();
    if (lastSuffix !== undefined)
    {
      var thisView = window["view" + thisSuffix];
      var lastView = window["view" + lastSuffix];
      var signals = [
        "nodeRadius", "linkWidth", "nodeCharge", "linkDistance",
        "linkStrength", "static", "sizeSelect", "colorSelect"
      ]
      for (i = 0; i < signals.length; i++)
        thisView.signal(signals[i], lastView.signal(signals[i]));
      thisView.runAsync();
    }
    lastSuffix = thisSuffix;
  }
  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.className += " active";
}

document.getElementsByClassName("tablinks")[0].click();
</script>

{% endblock %}
"""

TABCONTENT = """
<div id="{{ tabtitle }}" class="tabcontent">

  <div id="nodeTable{{ suffix }}"></div>
  <button onclick="exportPNG{{ suffix }}()">Download as PNG</button>
  <p></p>
  <div id="view{{ suffix }}"></div>
  <script type="text/javascript">
    var spec = {{ spec }};
    var view{{ suffix }};

    render{{ suffix }}(spec).catch(err => console.error(err));

    var firstDatum = view{{ suffix }}.data('node-data')[0];
    firstDatum = JSON.parse(JSON.stringify(firstDatum));
    for (const key in firstDatum) {
      firstDatum[key] = "&lt select a node to display &gt";
    }
    var firstNodeSelect = {"datum": firstDatum};
    drawTable{{ suffix }}("", firstNodeSelect);
    view{{ suffix }}.addSignalListener('nodeSelect', drawTable{{ suffix }});

    function drawTable{{ suffix }}(name, value) {
      var table = document.createElement("TABLE");
      table.classList.add("dataframe");
      table.classList.add("table");
      table.classList.add("table-striped");
      table.classList.add("table-hover");

      for (const key in value.datum) {
        if (key == "index" || key.startsWith('Taxon Level')) {
            continue;
        }
        row = table.insertRow(-1);
        var cell = row.insertCell(-1)
        cell.innerHTML = key
        cell = row.insertCell(-1)
        cell.innerHTML = value.datum[key]
      }

      var nodeTable = document.getElementById("nodeTable{{ suffix }}");
      nodeTable.innerHTML = "";
      nodeTable.appendChild(table);
    }

    function render{{ suffix }}(spec) {
      view{{ suffix }} = new vega.View(vega.parse(spec), {
        renderer:  'svg',  // renderer (canvas or svg)
        container: '#view{{ suffix }}',   // parent DOM container
        hover:     true       // enable hover processing
      });
      return view{{ suffix }}.runAsync();
    }

    /* thanks https://stackoverflow.com/a/70395566 */
    function exportPNG{{ suffix }}(){
      view{{ suffix }}.toImageURL('png').then(function(url) {
        var link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('target', '_blank');
        link.setAttribute('download', 'network.png');
        link.dispatchEvent(new MouseEvent('click'));
      }).catch(err => console.error(err));
    }
  </script>
</div>
"""

TABLECONTENT = """
<div id="{{ tabtitle }}" class="tabcontent">
{{ table }}
</div>
"""


def graph_to_spec(network):
    with open(TEMPLATES / "force-directed-layout.vg.json") as fh:
        spec = json.load(fh)

    attributes = pd.DataFrame([r for _, r in network.nodes(data=True)])
    colour_options = ["None"]
    size_options = ["None"]
    for key in attributes.columns:
        try:
            attributes[key].astype(float)
            size_options.append(key)
            continue
        except (ValueError, TypeError):
            pass
        if key != "Feature":
            colour_options.append(key)

    size_selector = {
        "name": "sizeSelect",
        "value": "None",
        "bind": {"input": "select", "name": "size ", "options": []},
    }
    size_selector["bind"]["options"] = size_options
    spec["signals"].insert(0, size_selector)

    colour_selector = {
        "name": "colorSelect",
        "value": "None",
        "bind": {"input": "select", "name": "color ", "options": []},
    }
    colour_selector["bind"]["options"] = colour_options
    spec["signals"].insert(0, colour_selector)

    nodes = nx.nodes(network)
    idx = {nid: i for i, nid in enumerate(nodes)}
    nodes = [{"index": idx[nid], **nodes[nid]} for nid in nodes]
    edges = nx.edges(network)
    links = [
        {"source": idx[n[0]], "target": idx[n[1]], **edges[n]} for n in edges
    ]
    for link in links:
        if "weight" in link:
            link["weight_sign"] = np.sign(link["weight"])
            link["weight"] = abs(link["weight"])
    # "group" in nodes is currently being used for colour
    # "value" in links has been dropped. not sure whether it did anything
    spec["data"] = [
        {"name": "node-data", "values": nodes},
        {"name": "link-data", "values": links},
    ]
    return spec


def get_connected_components(network):
    network = nx.to_undirected(network)
    groups = defaultdict(list)
    pairs = []
    singles = []
    components = [
        network.subgraph(c).copy() for c in nx.connected_components(network)
    ]
    for subgraph in components:
        order = subgraph.order()
        if order == 1:
            for nid, attr in subgraph.nodes(data=True):
                singles.append(attr["Feature"])
        elif order == 2:
            pair = [a["Feature"] for _, a in subgraph.nodes(data=True)]
            pairs.append(pair)
        else:
            groups[order].append(subgraph)
    orders = list(groups.keys())
    orders.sort(reverse=True)
    groups = [g for o in orders for g in groups[o]]
    return groups, pairs, singles


def create_html_file(directory, source_file, title, content):
    tab = {"url": source_file, "title": title}
    path = directory / source_file
    with open(path, "w") as fh:
        fh.write(content)
    return path, tab


def add_taxonomy_levels(row):
    taxonomy = []
    for level, label in enumerate(row["Taxon"].split(";"), 1):
        taxonomy.append(label)
        row[f"Taxon Level {level}"] = ";".join(taxonomy)
    return row


def annotate_with_metadata(network, metadata):
    metadata = metadata.to_dataframe()
    if "Taxon" in metadata.columns:
        metadata = metadata.apply(add_taxonomy_levels, axis=1)
        metadata = metadata.transpose().fillna(method="pad").transpose()
    attributes = {}
    for nid, attr in network.nodes(data=True):
        name = attr["Feature"]
        if name in metadata.index:  # fail silently if not present
            attributes[nid] = metadata.loc[name]
        # SpiecEasi prepends 'X' to names starting with numbers
        elif (
            len(name) > 1
            and name[0] == "X"
            and name[1] in "0123456789"
            and name[1:] in metadata.index
        ):
            attributes[nid] = {"Feature": name[1:], **metadata.loc[name[1:]]}
    nx.set_node_attributes(network, attributes)


def annotate_node_stats(network):
    dd = nx.degree_centrality(network)
    nx.set_node_attributes(network, dd, "Degree Centrality")
    bb = nx.betweenness_centrality(network)
    nx.set_node_attributes(network, bb, "Betweenness Centrality")
    cc = nx.closeness_centrality(network)
    nx.set_node_attributes(network, cc, "Closeness Centrality")
    ee = nx.eigenvector_centrality(network)
    nx.set_node_attributes(network, ee, "Eigenvector Centrality")
    ee = nx.assortativity.average_neighbor_degree(network)
    nx.set_node_attributes(network, ee, "Associativity")


def render_table(tab_buttons, tab_contents, tabtitle, table):
    button = TABBUTTON.replace("{{ tabtitle }}", tabtitle)
    tab_buttons.append(button)

    table = q2templates.df_to_html(table, index=False)
    content = TABLECONTENT.replace("{{ tabtitle }}", tabtitle)
    content = content.replace("{{ table }}", table)
    tab_contents.append(content)


def visualise_network(
    output_dir: str, network: nx.Graph, metadata: qiime2.Metadata = None
) -> None:

    if metadata:
        annotate_with_metadata(network, metadata)

    annotate_node_stats(network)

    q2templates.util.copy_assets(
        TEMPLATES / "assets", Path(output_dir) / "assets"
    )

    with tempfile.TemporaryDirectory() as temp_dir_name:
        groups, pairs, singles = get_connected_components(network)

        tab_buttons = []
        tab_contents = []
        for i, graph in enumerate(groups):
            tabtitle = f"Group {i+1}"

            button = TABBUTTON.replace("{{ tabtitle }}", tabtitle)
            tab_buttons.append(button)

            spec = json.dumps(graph_to_spec(graph), indent=1)
            content = TABCONTENT.replace("{{ tabtitle }}", tabtitle)
            content = content.replace("{{ suffix }}", f"{i+1}")
            content = content.replace("{{ spec }}", spec)
            tab_contents.append(content)

        if pairs:
            table = pd.DataFrame(pairs, columns=["Feature 1", "Feature 2"])
            render_table(tab_buttons, tab_contents, "Pairs", table)

        if singles:
            table = pd.DataFrame(singles, columns=["Feature"])
            render_table(tab_buttons, tab_contents, "Singles", table)

        content = INDEX.replace("{{ tabbuttons }}", "\n".join(tab_buttons))
        content = content.replace("{{ tabcontents }}", "\n".join(tab_contents))

        temp_dir = Path(temp_dir_name)
        source_file = temp_dir / "index.html"
        with open(source_file, 'w') as fh:
            fh.write(content)

        q2templates.render(
            [source_file],
            output_dir,
            context={"title": "Networks"}
        )
