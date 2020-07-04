import logging

_log = logging.getLogger(__name__)

_plugin_name_ = 'plaintext-passwords'


def scan(container, output_queue):
    """Plugin scan all logs file and try to find any plaintext credentials.

    :param container: Container to process data for.
    :param output_queue: Output holder for this plugin.

    :return: This plugin returns the object in this form.
    {
        _plugin_name_: object
    }
    """

    res = {}

    _log.info('Staring {} Plugin ...'.format(_plugin_name_))

    passwords_regex = "pwd|password|pass|secret"

    files = {
        "LOG_FILES": {
            "cmd": "find / -name '*.log' | xargs egrep -Hi "
                   "'" + passwords_regex + "'",
            "msg": "Check all *.log files",
            "results": []
        },
        "CONFIG_FILES": {
            "cmd": "find / -name '*.c*' | xargs egrep -Hi "
                   "'" + passwords_regex + "'",
            "msg": "Check all Config files",
            "results": []
        },
        "YML_FILES": {
            "cmd": "find / -name '*.yml' | xargs egrep "
                   "-Hi '" + passwords_regex + "'",
            "msg": "Check all Config files",
            "results": []
        },
        "YAML_FILES": {
            "cmd": "find / -name '*.yaml' | xargs egrep "
                   "-Hi '" + passwords_regex + "'",
            "msg": "Check all Config files",
            "results": []
        },
        "APP_PROPERTIES": {
            "cmd": "find / -name '*.properties' | xargs egrep "
                   "-Hi '" + passwords_regex + "'",
            "msg": "Check all properties files",
            "results": []
        },
        "SHADOW": {
            "cmd": "cat /etc/shadow",
            "msg": "Check Shadow file",
            "results": []
        }

    }

    command_list = list(files.keys())

    for item in command_list:
        cmd = "sh -c " + "\"" + files[item]['cmd'] + "\""
        command_result = container.exec_run(
            cmd=cmd,
            stderr=False,
            stdin=False)

        # If command is not executed successfully, dont show in output
        if command_result.exit_code != 0:
            del files[item]
            continue

        output = command_result.output.decode('utf-8')
        result = output.split('\n')
        files[item]['results'] = result
        del files[item]['cmd']

    result = files

    res[container.short_id] = {
        _plugin_name_: result
    }

    _log.info('Completed execution of {} Plugin.'.format(_plugin_name_))
    output_queue.put(res)
