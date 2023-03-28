from xml.etree.ElementTree import ParseError

import qiime2.plugin
import qiime2.plugin.model as model
from networkx import Graph, read_graphml
from qiime2.plugin import ValidationError


class NetworkFormat(model.TextFileFormat):
    def _validate_(self, level):
        try:
            network = read_graphml(str(self))
            if not isinstance(network, Graph):
                raise ValidationError("no graph in network file")
        except ParseError as err:
            raise ValidationError("bad network file") from err


NetworkDirectoryFormat = model.SingleFileDirectoryFormat(
    "NetworkDirectoryFormat", "network.graphml", NetworkFormat
)

Network = qiime2.plugin.SemanticType("Network")
