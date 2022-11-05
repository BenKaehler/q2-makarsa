import json
from pathlib import Path
import pkg_resources

import q2templates

TEMPLATES = Path(pkg_resources.resource_filename('q2_SpiecEasi', 'assets'))


def visualise_network(
        output_dir: str = None):
    title = 'SpiecEasi Network'
    index = TEMPLATES / 'index.html'
    with open(TEMPLATES / 'miserables.json') as fh:
        data = json.load(fh)
    with open(TEMPLATES / 'force-directed-layout.vg.json') as fh:
        spec = json.load(fh)
    spec["data"] = [
        {
          "name": "node-data",
          "values": data["nodes"]
        },
        {
          "name": "link-data",
          "values": data["links"]
        }]

    q2templates.render([index], output_dir, context={
        'title': title, 'spec': json.dumps(spec, indent=1)})
