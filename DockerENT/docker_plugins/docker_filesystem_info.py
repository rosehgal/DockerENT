"""Docker file-system-info scan plugin."""
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

    _log.info('Staring {} Plugin ...'.format(_plugin_name_))

    driveinfo = {
        "MOUNT": {
            "cmd": "mount",
            "msg": "Mount results",
            "results": []
        },
        "FSTAB": {
            "cmd": "cat /etc/fstab",
            "msg": "fstab entries",
            "results": []
        }
    }

    for item in driveinfo:
        cmd = driveinfo[item]['cmd']
        output = container.exec_run(cmd).output.decode('utf-8')
        result = output.split('\n')
        driveinfo[item]['results'] = result
        del driveinfo[item]['cmd']

    result = driveinfo

    res[container.short_id] = {
        _plugin_name_: result
    }

    _log.info('Completed execution of {} Plugin.'.format(_plugin_name_))
    output_queue.put(res)
