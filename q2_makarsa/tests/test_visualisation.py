import os
import tempfile
from pathlib import Path

import networkx as nx
from networkx import read_graphml
import networkx.algorithms.isomorphism as iso
import pandas as pd
from qiime2 import Metadata
from qiime2.plugin.testing import TestPluginBase

from q2_makarsa._visualisation import (
    get_connected_components, graph_to_spec, create_html_file,
    add_taxonomy_levels, annotate_with_metadata, annotate_node_stats,
    render_table, visualise_network)

import json


class GraphEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, nx.Graph):
            return nx.node_link_data(obj)
        return json.JSONEncoder.default(self, obj)


class TestVisualiseNetwork(TestPluginBase):
    package = "q2_makarsa.tests"

    def setUp(self):
        super().setUp()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp_dir.name)
        self.network = read_graphml(self.get_data_path("network.graphml"))

    def load_json(self, filename):
        with open(self.get_data_path(filename)) as fh:
            return json.load(fh)

    def assertObjectEqual(self, obj1, obj2):  # thanks ChatGPT
        """Test equality of two objects, accounting for numeric tolerance."""
        if (isinstance(obj1, (float, complex)) and
                isinstance(obj2, (float, complex))):
            # Check for numerical equality with tolerance
            self.assertAlmostEqual(obj1, obj2)
        elif isinstance(obj1, dict) and isinstance(obj2, dict):
            # Recursively check each key-value pair in the dictionaries
            self.assertEqual(obj1.keys(), obj2.keys())
            for key in obj1.keys():
                self.assertObjectEqual(obj1[key], obj2[key])
        elif isinstance(obj1, list) and isinstance(obj2, list):
            # Recursively check each element in the lists
            self.assertEqual(len(obj1), len(obj2))
            for element1, element2 in zip(obj1, obj2):
                self.assertObjectEqual(element1, element2)
        else:
            # For non-numeric or non-dict/list types, use regular assertion
            self.assertEqual(obj1, obj2)

    def test_graph_to_spec(self):
        graphs, pairs, singles = get_connected_components(self.network)
        observed = graph_to_spec(graphs[0])
        expected = self.load_json("spec.json")
        self.assertObjectEqual(observed, expected)

    def test_get_connected_components(self):
        network = nx.Graph()
        network.add_edges_from([(1, 2), (2, 3), (4, 5), (5, 6), (7, 8)])
        network.add_nodes_from([9, 10])
        attributes = {n: {"Feature": n} for n in network}
        nx.set_node_attributes(network, attributes)
        groups, pairs, singles = get_connected_components(network)

        self.assertEqual(len(groups), 2)
        self.assertEqual(len(pairs), 1)

        self.assertTrue(
            iso.is_isomorphic(groups[0], network.subgraph([1, 2, 3])))
        self.assertTrue(
            iso.is_isomorphic(groups[1], network.subgraph([4, 5, 6])))
        self.assertEqual(set(pairs[0]), {7, 8})
        self.assertEqual(set(singles), {9, 10})

    def test_create_html_file(self):  # thanks ChatGPT
        source_file = "example.html"
        title = "Example"
        content = "<html><head><title>Example</title></head>"\
            "<body><p>Hello, world!</p></body></html>"
        path, tab = create_html_file(
            self.directory, source_file, title, content)
        self.assertTrue(os.path.isfile(path))
        with open(path, "r") as f:
            self.assertEqual(f.read(), content)
        self.assertEqual(tab, {"url": source_file, "title": title})

    def test_annotate_with_metadata(self):  # based on ChatGPT suggestion
        # Create a simple network with two nodes
        network = nx.Graph()
        network.add_node(0, Feature="Feature1")
        network.add_node(1, Feature="Feature2")
        # Create a simple metadata table
        metadata = pd.DataFrame(
            {"Taxon": {"Feature1": "A", "Feature2": "B"}})
        metadata.index.name = 'feature-id'
        metadata = Metadata(metadata)
        # Run annotate_with_metadata
        annotate_with_metadata(network, metadata)
        # Check that the network nodes have the expected attributes
        self.assertEqual(network.nodes[0]["Taxon"], "A")
        self.assertEqual(network.nodes[1]["Taxon"], "B")

    def test_annotate_node_stats(self):  # thanks ChatGPT
        # Create a test network
        network = nx.barbell_graph(5, 1)

        # Call the function to annotate node stats
        annotate_node_stats(network)

        # Check that the expected attributes have been added to the nodes
        for node_id in network.nodes:
            self.assertTrue("Degree Centrality" in network.nodes[node_id])
            self.assertTrue("Betweenness Centrality" in network.nodes[node_id])
            self.assertTrue("Closeness Centrality" in network.nodes[node_id])
            self.assertTrue("Eigenvector Centrality" in network.nodes[node_id])
            self.assertTrue("Associativity" in network.nodes[node_id])

    def test_visualise_network(self):  # thanks ChatGPT
        network = nx.Graph()
        network.add_node(0, Feature="Feature1")
        network.add_node(1, Feature="Feature2")
        metadata = pd.DataFrame(
            {"Taxon": {"Feature1": "A", "Feature2": "B"}})
        metadata.index.name = 'feature-id'
        metadata = Metadata(metadata)

        output_dir = self.directory / 'viz_output'
        os.makedirs(output_dir)
        visualise_network(output_dir, network, metadata)

        self.assertTrue((output_dir / 'index.html').exists())
        self.assertTrue((output_dir / 'assets' / 'css' / 'tabs.css').exists())
        self.assertTrue((output_dir / 'assets' / 'css' / 'vega.css').exists())

    def test_render_table(self):
        tab_buttons = []
        tab_contents = []

        table = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})

        tabtitle = "test"
        render_table(tab_buttons, tab_contents, tabtitle, table)

        self.assertEqual(
            tab_buttons[0],
            '''
<button class="tablinks" onclick="openTab(event, 'test')">
test</button>
''')
        self.assertEqual(
            tab_contents[0], '''
<div id="test" class="tabcontent">
<table border="0" class="dataframe table table-striped table-hover">
  <thead>
    <tr style="text-align: right;">
      <th>a</th>
      <th>b</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>3</td>
    </tr>
    <tr>
      <td>2</td>
      <td>4</td>
    </tr>
  </tbody>
</table>
</div>
''')

    def test_add_taxonomy_levels(self):  # thanks ChatGPT
        # Define test input data
        data = {
            "Taxon": ["A;B;C", "D;E;F"],
        }
        df = pd.DataFrame(data)

        # Apply function to test data
        df = df.apply(add_taxonomy_levels, axis=1)

        # Define expected output data
        expected_data = {
            "Taxon": ["A;B;C", "D;E;F"],
            "Taxon Level 1": ["A", "D"],
            "Taxon Level 2": ["A;B", "D;E"],
            "Taxon Level 3": ["A;B;C", "D;E;F"],
        }
        expected_df = pd.DataFrame(expected_data)

        # Check that the output matches the expected output
        pd.testing.assert_frame_equal(df, expected_df)

    def tearDown(self):
        self.temp_dir.cleanup()
