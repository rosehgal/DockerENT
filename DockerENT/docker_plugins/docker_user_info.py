import logging

_log = logging.getLogger(__name__)

_plugin_name_ = 'user-info'


def scan(container, output_queue):
    """Plugin to perform checks on user jobs.

    :param container: Container to process data for.
    :param output_queue: Output holder for this plugin.

    :return: This plugin returns the object in this form.
    {
        _plugin_name_: object
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

    for item in userinfo:
        cmd = userinfo[item]['cmd']
        output = container.exec_run(cmd).output.decode('utf-8')
        result = output.split('\n')
        userinfo[item]['results'] = result
        del userinfo[item]['cmd']

    result = userinfo

    res[container.short_id] = {
        _plugin_name_: result
    }

    _log.info('Completed execution of {} Plugin.'.format(_plugin_name_))
    output_queue.put(res)
