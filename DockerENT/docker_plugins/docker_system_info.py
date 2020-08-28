"""Docker system info scan plugin."""
import logging

_log = logging.getLogger(__name__)

_plugin_name_ = 'sysinfo'


def scan(container, output_queue, audit=False, audit_queue=None):
    """Docker system-info scan plugin.

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

    sysinfo = {
        "OS": {
            "cmd": "cat /etc/issue",
            "msg": "Operating System",
            "results": []
        },
        "KERNEL": {
            "cmd": "cat /proc/version",
            "msg": "Kernel",
            "results": []
        },
        "HOSTNAME": {
            "cmd": "hostname",
            "msg": "Hostname",
            "results": []}
    }

    for item in sysinfo:
        cmd = sysinfo[item]['cmd']
        output = container.exec_run(cmd).output.decode('utf-8')

        sysinfo[item]['results'] = output
        del sysinfo[item]['cmd']

    result = sysinfo

    res[container.short_id] = {
        _plugin_name_: result
    }

    _log.info('Completed execution of {} Plugin.'.format(_plugin_name_))
    output_queue.put(res)
