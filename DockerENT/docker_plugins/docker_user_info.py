"""Docker user info scan plugin."""
from DockerENT.utils import utils
import logging

_log = logging.getLogger(__name__)

_plugin_name_ = 'user-info'


def scan(container, output_queue, audit=False, audit_queue=None):
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

    if audit:
        _audit(container, userinfo, audit_queue)


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
        "WHOAMI": {
            'weak_conf': ['root', 'admin', 'superuser'],
            'warn_msg': 'Current USER is : '
        },
        "ALLUSERS": {
            'safe_conf': [],
            'warn_msg': 'User with password in passwd file: '
        },
        "SUDOERS": {
            "safe_conf": [],
            "warn_message": 'Sudoers found : '
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
                    if security_option == 'ALLUSERS':
                        plain_text_creds = []

                        for ar in actual_results:
                            result_list = ar.split(':')
                            if len(result_list) > 1 and (
                                    result_list[1] != '!' and
                                    result_list[1] != '*' and
                                    result_list[1] != 'x'):
                                plain_text_creds.append(ar)

                        if plain_text_creds:
                            r = columns + [warn_message + ";".join(
                                plain_text_creds
                            )]
                            audit_report[container_id].append(", ".join(r))
            else:
                issues = utils.list_intersection(
                    actual_results, weak_results)
                if issues != []:
                    # Weak configuration detected
                    r = columns + [warn_message + ";".join(issues)]
                    audit_report[container_id].append(
                        ", ".join(r)
                    )

    audit_queue.put(audit_report)
