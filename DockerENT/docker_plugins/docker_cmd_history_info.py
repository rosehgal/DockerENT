import logging

_log = logging.getLogger(__name__)

_plugin_name_ = 'user-command-history'


def scan(container, output_queue):
    """Plugin to check the user history.

    :param container: Container to process data for.
    :param output_queue: Output holder for this plugin.

    :return: This plugin returns the object in this form.
    {
        _plugin_name_: object
    }
    """

    res = {}

    _log.info('Staring {} Plugin ...'.format(_plugin_name_))

    historyfiles = {
        "ROOT_HISTORY": {
            "cmd": "ls -la /root/.*_history",
            "msg": "See if you have access too Root user history (depends on "
                   "privs)",
            "results": []
        },
        "BASH_HISTORY": {
            "cmd": "cat ~/.bash_history",
            "msg": "Get the contents of bash history file for current user",
            "results": []
        },
        "NANO_HISTORY": {
            "cmd": "cat ~/.nano_history",
            "msg": "Try to get the contents of nano history file for current "
                   "user",
            "results": []
        },
        "ATFTP_HISTORY": {
            "cmd": "cat ~/.atftp_history",
            "msg": "Try to get the contents of atftp history file for current "
                   "user",
            "results": []
        },
        "MYSQL_HISTORY": {
            "cmd": "cat ~/.mysql_history",
            "msg": "Try to get the contents of mysql history file for current "
                   "user",
            "results": []
        },
        "PHP_HISTORY": {
            "cmd": "cat ~/.php_history",
            "msg": "Try to get the contents of php history file for current "
                   "user",
            "results": []
        },
        "PYTHON_HISTORY": {
            "cmd": "cat ~/.python_history",
            "msg": "Try to get the contents of python history file for "
                   "current user",
            "results": []
        },
        "REDIS_HISTORY": {
            "cmd": "cat ~/.rediscli_history",
            "msg": "Try to get the contents of redis cli history file for "
                   "current user",
            "results": []
        },
        "TDSQL_HISTORY": {
            "cmd": "cat ~/.tdsql_history",
            "msg": "Try to get the contents of tdsql history file for current "
                   "user",
            "results": []
        }
    }

    command_list = list(historyfiles.keys())

    for item in command_list:
        cmd = historyfiles[item]['cmd']
        command_result = container.exec_run(
            cmd=cmd.split(' '),
            stderr=False,
            stdin=False)

        # If command is not executed successfully, dont show in output
        if command_result.exit_code != 0:
            del historyfiles[item]
            continue

        output = command_result.output.decode('utf-8')
        result = output.split('\n')
        historyfiles[item]['results'] = result
        del historyfiles[item]['cmd']

    result = historyfiles

    res[container.short_id] = {
        _plugin_name_: result
    }

    _log.info('Completed execution of {} Plugin.'.format(_plugin_name_))
    output_queue.put(res)
