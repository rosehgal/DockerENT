"""Docker plaintext password in configs scan plugin."""
from DockerENT import utils
import logging

_log = logging.getLogger(__name__)

_plugin_name_ = 'plaintext-passwords'


def scan(container, output_queue, audit=False, audit_queue=None):
    """Docker plaintext password scan plugin.

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

    if audit:
        _audit(container, files, audit_queue)


def _audit(container, scan_report, audit_queue):
    """Perform Scan audit.

    :param scan_report: dict
    :param audit_queue: Multiprocessing queue to perform Audit.
    """
    container_id = container.short_id
    audit_report = {}
    audit_report[container_id] = []

    columns = [_plugin_name_, 'WARN']

    weak_configurations = {
        "LOG_FILES": {
            'safe_conf': [],
            'warn_msg': 'Password Identified in LOG files: '
        },
        "CONFIG_FILES": {
            'safe_conf': [],
            'warn_msg': 'Password Identified in CONFIG files: '
        },
        "YML_FILES": {
            'safe_conf': [],
            'warn_msg': 'Password Identified in YML files: '
        },
        "YAML_FILES": {
            'safe_conf': [],
            'warn_msg': 'Password Identified in YAML files: '
        },
        "APP_PROPERTIES": {
            'safe_conf': [],
            'warn_msg': 'Password Identified in PROP files: '
        },
        "SHADOW": {
            'safe_conf': [],
            'warn_msg': 'Password Identified in SHADOW files: '
        }
    }

    for security_option in scan_report.keys():
        if security_option in weak_configurations.keys():
            actual_results = scan_report[security_option]['results']
            weak_results = None
            safe_results = None

            if 'weak_conf' in weak_configurations[security_option].keys():
                weak_results = weak_configurations[security_option]['weak_conf']

            if 'safe_conf' in weak_configurations[security_option].keys():
                safe_results = weak_configurations[security_option]['safe_conf']

            warn_message = weak_configurations[security_option]['warn_msg']

            # If safe_conf, check on safe_conf else check on weak_conf
            if safe_results is not None:
                if actual_results != safe_results:
                    if security_option == 'SHADOW':
                        plain_text_creds = []

                        for ar in actual_results:
                            result_list = ar.split(':')
                            if len(result_list) > 1 and (
                                    result_list[1] != '!' and result_list[1] != '*'):
                                plain_text_creds.append(ar)

                        if plain_text_creds:
                            r = columns + [warn_message + ";".join(
                                plain_text_creds
                            )]
                            audit_report[container_id].append(", ".join(r))
                    else:
                        _r = [res for res in actual_results if res]
                        if _r:
                            r = columns + [warn_message + ";".join(_r)]
                            audit_report[container_id].append(", ".join(r))
            else:
                if utils.list_intersection(actual_results, weak_results) != []:
                    # Weak configuration detected
                    r = columns + [warn_message]
                    audit_report[container_id].append(
                        ", ".join(r)
                    )

    audit_queue.put(audit_report)
