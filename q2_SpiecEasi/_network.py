import qiime2.plugin.model as model
from qiime2.plugin import ValidationError
from scipy.io import mmread, mmwrite
from scipt.sparse import coo_matrix

from .plugin_setup import plugin


class NetworkFormat(model.BinaryFileFormat):
    def _validate_(self, level):
        try:
            matrix = mmread(str(self))
            if len(matrix.shape) != 2 or matrix.shape[0] != matrix.shape[1]:
                raise ValidationError("adjacency matrix is not square")
            if not isinstance(matrix, coo_matrix):
                raise ValidationError("adjacency matrix is not sparse")
        except ValueError as err:
            raise ValidationError("bad matrix file") from err


NetworkDirectoryFormat = model.SingleFileDirectoryFormat(
    'NetworkDirectoryFormat', 'adjacency_matrix.mtx', NetworkFormat)


@plugin.register_transformer
def _1(matrix: coo_matrix) -> (NetworkFormat):
    ff = NetworkFormat()
    mmwrite(str(ff))
    return ff


@plugin.register_transformer
def _2(ff: NetworkFormat) -> coo_matrix:
    return mmread(str(ff))
