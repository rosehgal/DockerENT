"""Docker network-info scan plugin."""
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

    netinfo = {
        "netinfo": {
            "cmd": "/sbin/ifconfig -a",
            "msg": "Interfaces",
            "results": []
        },
        "ROUTE": {
            "cmd": "route",
            "msg": "Route(s)",
            "results": []
        },
        "NETSTAT": {
            "cmd": "netstat -antup",
            "msg": "Netstat",
            "results": []
        }
    }

    for item in netinfo:
        cmd = netinfo[item]['cmd']
        output = container.exec_run(cmd).output.decode('utf-8')
        result = output.split('\n')
        netinfo[item]['results'] = result
        del netinfo[item]['cmd']

    result = netinfo

    res[container.short_id] = {
        _plugin_name_: result
    }

    _log.info('Completed execution of {} Plugin.'.format(_plugin_name_))
    output_queue.put(res)
