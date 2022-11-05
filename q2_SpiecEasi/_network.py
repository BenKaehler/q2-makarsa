import qiime2.plugin.model as model
from qiime2.plugin import ValidationError
from scipy.io import mmread
from scipy.sparse import coo_matrix

import qiime2.plugin


class NetworkFormat(model.TextFileFormat):
    def _validate_(self, level):
        try:
            with open(str(self)) as fh:
                matrix = mmread(fh)
            if len(matrix.shape) != 2 or matrix.shape[0] != matrix.shape[1]:
                raise ValidationError("adjacency matrix is not square")
            if not isinstance(matrix, coo_matrix):
                raise ValidationError("adjacency matrix is not sparse")
        except ValueError as err:
            raise ValidationError("bad matrix file") from err


NetworkDirectoryFormat = model.SingleFileDirectoryFormat(
    'NetworkDirectoryFormat', 'adjacency_matrix.mtx', NetworkFormat)

Network = qiime2.plugin.SemanticType('Network')
