"""HTML output plugin.

Process the records and write the content to the html file which can show
docker connects as networks. This file uses a templates called as template.html
"""
import jinja2
import json
import logging

_log = logging.getLogger(__name__)

_plugin_name_ = 'HTML_output_plugin'


def write(queue, filename='out.html'):
    """Plugin to create beautiful html file for output.

    :param queue: The input queue which contains the data from various scan
        plugins.
    :type queue: multiprocessing.managers.AutoProxy[Queue]

    :param filename: Name of file to output to.
    :type filename: str

    :return: None
    """
    _log.info('Writing to {} ...'.format(filename))

    nodes = []
    edges = []

    report = {}
    while not queue.empty():
        result = queue.get()
        for key in result.keys():
            if key in report.keys():
                report[key].append(result[key])
            else:
                report[key] = []
                report[key].append(result[key])

    """
    After processing the list would look something like this.
    {
      "3911e81b25": [
        {
          "sample": {
            "status": "good"
          }
        }
      ]
    }
    """
    group = -1
    for docker_node in report.keys():
        group += 1
        nodes.append(
            {
                'id': docker_node,
                'shape': 'image',
                'image': 'https://www.docker.com/sites/default/files/d8/2019'
                         '-07/Moby-logo.png',
                'label': docker_node,
                'pluginname': docker_node,
                'data': 'This is docker node',
                'labelHighlightBold': True,
            }
        )
        for plugin_node in report[docker_node]:
            for plugin_data_node in plugin_node.keys():
                node_id = 'plugin_' + plugin_data_node + '_' + docker_node
                nodes.append(
                    {
                        'id': node_id,
                        'shape': 'dot',
                        'label': plugin_data_node,
                        'pluginname': plugin_data_node,
                        'data': 'This is plugin node',
                        'labelHighlightBold': True,

                    }
                )

                edges.append(
                    {
                        'from': docker_node,
                        'to': node_id,
                        'length': 200
                    }
                )

                for cmd_node in plugin_node[plugin_data_node].keys():
                    child_node_id = docker_node + '_' + cmd_node
                    nodes.append(
                        {
                            'id': child_node_id,
                            'shape': 'dot',
                            'label': cmd_node,
                            'pluginname': cmd_node,
                            'data': plugin_node[plugin_data_node][cmd_node][
                                'results'],
                            'labelHighlightBold': True,
                            'group': group,
                        }
                    )
                    edges.append(
                        {
                            'from': node_id,
                            'to': child_node_id,
                            'value': 5,
                            'length': 100
                        }
                    )

    with open(filename, 'w+') as outfile, \
            open('DockerENT/output_plugins/template.html', 'r') as template:

        template_html = jinja2.Template(template.read())
        html = template_html.render(
            nodes=json.dumps(nodes),
            edges=json.dumps(edges)
        )
        outfile.write(html)
