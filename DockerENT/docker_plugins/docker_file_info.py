"""Docker file-system-info scan plugin."""
from DockerENT.utils import utils

import docker
import logging
import json

_log = logging.getLogger(__name__)

_plugin_name_ = 'files-info'


def scan(container, output_queue, audit=False, audit_queue=None):
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

    _log.info('Starting {} Plugin ...'.format(_plugin_name_))

    api_client = docker.APIClient()
    docker_inspect_output = api_client.inspect_container(container.short_id)

    fileinfo = {
        "WWDIRSROOT": {
            "isDockerAttribute": False,
            "cmd": "find /  -wholename '/home/' -prune  -user root -o  -type d -perm -0002 -exec ls -ld '{}' ';'",
            "msg": "World Writeable Directories for User/Group 'Root'",
            "results": []
        },
        "WWDIRS": {
            "isDockerAttribute": False,
            "cmd": "find / \( -wholename '/home/' -prune \) -user root -o \( -type d -perm -0002 \) -exec ls -ld '{}' ';'",
            "msg": "World Writeable Directories for Users other than Root",
            "results": []
        },
        "WWFILES": {
            "isDockerAttribute": False,
            "cmd": "find / \( -wholename '/home/' -prune -user root -o -wholename '/proc/' -prune \) -o \( -type f -perm -0002 \) -exec ls -l '{}' ';'",
            "msg": "World Writable Files",
            "results": []
        },
        "SUID": {
            "isDockerAttribute": False,
            "cmd": "find / \( -perm -2000 -o -perm -4000 \) -exec ls -ld {} \;",
            "msg": "SUID/SGID Files and Directories",
            "results": []
        },
        "ROOTHOME": {
            "isDockerAttribute": False,
            "cmd": "ls -ahlR /root",
            "msg": "Checking if root's home folder is accessible",
            "results": []
        }
    }

    for item in fileinfo.keys():
        if fileinfo[item]['isDockerAttribute']:
            option_result = utils.get_value_from_str_dotted_key(
                docker_inspect_output,
                fileinfo[item]['attribute_name']
            )
            del fileinfo[item]['attribute_name']

            # Key not found
            if option_result is None:
                del fileinfo[item]['isDockerAttribute']
                continue
            elif isinstance(option_result, list):
                fileinfo[item]['results'].extend(option_result)
            else:
                fileinfo[item]['results'].append(option_result)

        else:
            cmd = fileinfo[item]['cmd']

            output = container.exec_run(cmd).output.decode('utf-8')

            result = output.split('\n')
            fileinfo[item]['results'] = result
            del fileinfo[item]['cmd']

        del fileinfo[item]['isDockerAttribute']

    result = fileinfo

    res[container.short_id] = {
        _plugin_name_: result
    }

    _log.info('Completed execution of {} Plugin.'.format(_plugin_name_))
    output_queue.put(res)

    if audit:
        # Perform Audit for this result
        _audit(container, fileinfo, audit_queue)


def _audit(container, scan_report, audit_queue):
    """Perform Scan audit.

    :param scan_report: dict
    :param audit_queue: Multiprocessing queue to perform Audit.
    """
    weak_configurations = {
        "WWDIRSROOT": {
            "safe_conf": [],
            "warn_msg": "World Writeable Directories for User/Group 'Root': ",
        },
        "WWDIRS": {
            "safe_conf": [],
            "warn_msg": "World Writeable Directories for Users other than Root",
        },
        "WWFILES": {
            "safe_conf": [],
            "warn_msg": "World Writable Files: ",
        },
        "SUID": {
            "safe_conf": [],
            "warn_msg": "SUID/SGID Files and Directories: ",
        },
        "ROOTHOME": {
            "safe_conf": [],
            "warn_msg": "Checking if root's home folder is accessible: ",
        }
    }

    container_id = container.short_id
    audit_report = {}
    audit_report[container_id] = []

    columns = [_plugin_name_, 'WARN']
    for security_option in scan_report.keys():
        if security_option in weak_configurations.keys():
            actual_results = scan_report[security_option]['results']
            if isinstance(actual_results, dict):
                actual_results = json.dumps(actual_results)

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
                for wr in weak_results:
                    if any(wr in ar for ar in actual_results):
                        # Weak configuration detected
                        r = columns + [warn_message]
                        audit_report[container_id].append(
                            ", ".join(r)
                        )

    audit_queue.put(audit_report)
