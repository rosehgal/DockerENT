"""Docker file-system-info scan plugin."""
from DockerENT.utils import utils

import docker
import logging

_log = logging.getLogger(__name__)

_plugin_name_ = 'file-system-info'


def scan(container, output_queue):
    """Docker file-system-info plugin scan.

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

    _log.info('Starting {} Plugin ...'.format(_plugin_name_))

    api_client = docker.APIClient()
    docker_inspect_output = api_client.inspect_container(container.short_id)

    driveinfo = {
        "MOUNT": {
            "isDockerAttribute": False,
            "cmd": "mount",
            "msg": "Mount results",
            "results": []
        },
        "FSTAB": {
            "isDockerAttribute": False,
            "cmd": "cat /etc/fstab",
            "msg": "fstab entries",
            "results": []
        },
        "RW_VOLUMES": {
            "isDockerAttribute": True,
            "attribute_name": "VolumesRW",
            "msg": "R/W volumes mounted in docker.",
            "results": []

        },
        "DOCKER_MOUNTS": {
            "isDockerAttribute": True,
            "attribute_name": "Mounts",
            "msg": "List mounted volumes in docker.",
            "results": []
        }
    }

    for item in driveinfo.keys():
        _log.info(item)
        if driveinfo[item]['isDockerAttribute']:
            option_result = utils.get_value_from_str_dotted_key(
                docker_inspect_output,
                driveinfo[item]['attribute_name']
            )
            del driveinfo[item]['attribute_name']

            # Key not found
            if option_result is None:
                del driveinfo[item]['isDockerAttribute']
                continue
            elif isinstance(option_result, list):
                driveinfo[item]['results'].extend(option_result)
            else:
                driveinfo[item]['results'].append(option_result)

        else:
            cmd = driveinfo[item]['cmd']
            output = container.exec_run(cmd).output.decode('utf-8')
            result = output.split('\n')
            driveinfo[item]['results'] = result
            del driveinfo[item]['cmd']

        del driveinfo[item]['isDockerAttribute']

    result = driveinfo

    res[container.short_id] = {
        _plugin_name_: result
    }

    _log.info('Completed execution of {} Plugin.'.format(_plugin_name_))
    output_queue.put(res)
