from xml.etree.ElementTree import ParseError

import qiime2.plugin
import qiime2.plugin.model as model
from networkx import Graph, read_graphml
from qiime2.plugin import ValidationError
import pandas as pd


class NetworkFormat(model.TextFileFormat):
    def _validate_(self, level):
        try:
            network = read_graphml(str(self))
        except ParseError as err:
            raise ValidationError("bad network file") from err
        if not isinstance(network, Graph):
            raise ValidationError("no graph in network file")
        for node in network.nodes():
            if "Feature" not in network.nodes[node]:
                raise ValidationError("nodes must have Feature attributes")


NetworkDirectoryFormat = model.SingleFileDirectoryFormat(
    "NetworkDirectoryFormat", "network.graphml", NetworkFormat
)

Network = qiime2.plugin.SemanticType("Network")


class NodeMapFormat(model.TextFileFormat):
    def _validate_(self, level):
        try:
            table = pd.read_table(str(self))
        except ParseError as err:
            raise ValidationError("bad node community table") from err
        if not isinstance(table, pd.DataFrame):
            raise ValidationError("no table in file")
        for thing in ('feature id', 'Community'):
            if thing not in table.columns:
                raise ValidationError(f"table does not include {thing}")


NodeDirectoryFormat = model.SingleFileDirectoryFormat(
    "NodeDirectoryFormat", "community.tsv", NodeMapFormat
)
NodeMap = qiime2.plugin.SemanticType("NodeMap")
