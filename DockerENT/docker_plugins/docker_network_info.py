"""Docker network-info scan plugin."""
from DockerENT.utils import utils

import docker
import logging

_log = logging.getLogger(__name__)

_plugin_name_ = 'netinfo'


def scan(container, output_queue):
    """Docker network-info plugin scan.

    :param container: container instance.
    :type container: docker.models.containers.Container

    :param output_queue: Output holder for this plugin.
    :type output_queue: multiprocessing.managers.AutoProxy[Queue]

    :return: This plugin returns the object in this form.
    {
        _plugin_name_: {
            'test_performed': {
                'results':  []
            }
        }
    }
    """
    res = {}

    _log.info('Staring {} Plugin ...'.format(_plugin_name_))

    api_client = docker.APIClient()
    docker_inspect_output = api_client.inspect_container(container.short_id)

    netinfo = {
        "NETINFO": {
            "isDockerInspectAttribute": False,
            "cmd": "/sbin/ifconfig -a",
            "msg": "Interfaces",
            "results": []
        },
        "ROUTE": {
            "isDockerInspectAttribute": False,
            "cmd": "route",
            "msg": "Route(s)",
            "results": []
        },
        "NETSTAT": {
            "isDockerInspectAttribute": False,
            "cmd": "netstat -antup",
            "msg": "Netstat",
            "results": []
        },
        "PORT_BINDINGS": {
            "isDockerInspectAttribute": True,
            "attribute_name": "NetworkSettings.Ports",
            "msg": "Docker port bindings",
            "results": []
        }
    }

    for item in netinfo.keys():
        if not netinfo[item]['isDockerInspectAttribute']:
            cmd = netinfo[item]['cmd']
            output = container.exec_run(cmd).output.decode('utf-8')
            result = output.split('\n')
            netinfo[item]['results'] = result
            del netinfo[item]['cmd']
        else:
            if netinfo[item]['isDockerInspectAttribute']:
                option_result = utils.get_value_from_str_dotted_key(
                    docker_inspect_output,
                    netinfo[item]['attribute_name']
                )
                del netinfo[item]['attribute_name']

                # Key not found
                if option_result is None:
                    del netinfo[item]['isDockerInspectAttribute']
                    continue
            # Output of docker inspect port is a map, with keys as
            netinfo[item]['results'].append(option_result)

        del netinfo[item]['isDockerInspectAttribute']

    result = netinfo

    res[container.short_id] = {
        _plugin_name_: result
    }

    _log.info('Completed execution of {} Plugin.'.format(_plugin_name_))
    output_queue.put(res)
