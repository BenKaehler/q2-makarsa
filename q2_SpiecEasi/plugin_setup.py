import importlib

import qiime2
from qiime2.plugin import Plugin

from ._visualisation import visualise_network


plugin = Plugin(
    name='spieceasi',
    version='0.0.0-dev',
    website='https://github.com/BenKaehler/q2-SpiecEasi/tree/main/q2_SpiecEasi',
    package='q2_SpiecEasi'
)

plugin.visualizers.register_function(
    function=visualise_network,
    inputs={},
    parameters={},
    name='Visualize network',
    description='Create an interactive depiction of your network.'
)

