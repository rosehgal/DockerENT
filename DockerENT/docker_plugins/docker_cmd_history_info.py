"""Docker command history scan plugin."""
from DockerENT import utils

import logging

_log = logging.getLogger(__name__)

_plugin_name_ = 'user-command-history'


def scan(container, output_queue, audit=False, audit_queue=None):
    """Docker command history plugin scan.

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

    historyfiles = {
        "ROOT_SH_HISTORY": {
            "cmd": 'cat /root/.ash_history',
            "msg": "See if you have access too Root user history (depends on "
                   "privs)",
            "results": []
        },
        "ROOT_BASH_HISTORY": {
            "cmd": 'cat /root/.bash_history',
            "msg": "See if you have access too Root user history (depends on "
                   "privs)",
            "results": []
        },
        "USER_SH_HISTORY": {
            "cmd": 'cat ~/.ash_history ',
            "msg": "Try to get history files for current user",
            "results": []
        },
        "USER_BASH_HISTORY": {
            "cmd": 'cat ~/.bash_history ',
            "msg": "Try to get history files for current user",
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

    if audit:
        _audit(container, historyfiles, audit_queue)


def _audit(container, scan_report, audit_queue):
    """Perform Scan audit.

    :param scan_report: dict
    :param audit_queue: Multiprocessing queue to perform Audit.
    """
    weak_configurations = {
        "ROOT_SH_HISTORY": {
            "warn_msg": "Root History present: ",
            "safe_conf": []
        },
        "ROOT_BASH_HISTORY": {
            "warn_msg": "Root History present: ",
            "safe_conf": []
        },
        "USER_SH_HISTORY": {
            "warn_msg": "USER BASH History present: ",
            "safe_conf": []
        },
        "USER_BASH_HISTORY": {
            "warn_msg": "USER BASH History present: ",
            "safe_conf": []
        },
        "NANO_HISTORY": {
            "warn_msg": "NANO History present: ",
            "safe_conf": []
        },
        "ATFTP_HISTORY": {
            "warn_msg": "ATFTP History present: ",
            "safe_conf": []
        },
        "MYSQL_HISTORY": {
            "warn_msg": "MySQL History present: ",
            "safe_conf": []
        },
        "PHP_HISTORY": {
            "warn_msg": "PHP History present: ",
            "safe_conf": []
        },
        "PYTHON_HISTORY": {
            "warn_msg": "Python History present: ",
            "safe_conf": []
        },
        "REDIS_HISTORY": {
            "warn_msg": "REDIS History present: ",
            "safe_conf": []
        },
        "TDSQL_HISTORY": {
            "warn_msg": "TDSQL History present: ",
            "safe_conf": []
        }
    }

    container_id = container.short_id
    audit_report = {}
    audit_report[container_id] = []
    columns = [_plugin_name_, 'WARN']

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
