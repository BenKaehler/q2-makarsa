import os
import json

import pkg_resources
import q2templates

TEMPLATES = pkg_resources.resource_filename('q2_SpiecEasi', 'assets')


def visualise_network(
        output_dir: str = None):
    # contexts = q2templates.df_to_html(caches, index=False)
    title = 'SpiecEasi Network'
    # EEEE change to new-style paths
    index = os.path.join(TEMPLATES, 'index.html')
    with open(os.path.join(TEMPLATES, 'miserables.json')) as fh:
        data = json.load(fh)
    with open(os.path.join(TEMPLATES, 'force-directed-layout.vg.json')) as fh:
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
