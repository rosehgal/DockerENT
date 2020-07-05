"""Docker user info scan plugin."""
import logging

_log = logging.getLogger(__name__)

_plugin_name_ = 'user-info'


def scan(container, output_queue):
    """Docker user-info scan plugin.

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
    userinfo = {
        "WHOAMI": {
            "cmd": "whoami",
            "msg": "Current User",
            "results": []
        },
        "ID": {
            "cmd": "id",
            "msg": "Current User ID",
            "results": []
        },
        "ALLUSERS": {
            "cmd": "cat /etc/passwd",
            "msg": "All users",
            "results": []
        },
        "ENV": {
            "cmd": "env",
            "msg": "Environment",
            "results": []
        },
        "SUDOERS": {
            "cmd": "cat /etc/sudoers",
            "msg": "Sudoers (privileged)",
            "results": []
        }
    }

    command_list = list(userinfo.keys())

    for item in command_list:
        cmd = "sh -c " + "\"" + userinfo[item]['cmd'] + "\""
        command_result = container.exec_run(
            cmd=cmd,
            stderr=True,
            stdin=False)

        # If command is not executed successfully, dont show in output
        if command_result.exit_code != 0:
            del userinfo[item]
            continue

        output = command_result.output.decode('utf-8')
        result = output.split('\n')
        userinfo[item]['results'] = result
        del userinfo[item]['cmd']

    result = userinfo

    res[container.short_id] = {
        _plugin_name_: result
    }

    _log.info('Completed execution of {} Plugin.'.format(_plugin_name_))
    output_queue.put(res)
