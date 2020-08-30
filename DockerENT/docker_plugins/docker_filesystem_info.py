"""Docker file-system-info scan plugin."""
from DockerENT.utils import utils

import docker
import logging
import json

_log = logging.getLogger(__name__)

_plugin_name_ = 'file-system-info'


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

    driveinfo = {
        "MOUNT": {
            "isDockerAttribute": False,
            "cmd": "mount",
            "msg": "Mount results",
            "results": []
        },
        "FSTAB": {
            "isDockerAttribute": False,
            "cmd": "cat /etc/fstab",
            "msg": "fstab entries",
            "results": []
        },
        "RW_VOLUMES": {
            "isDockerAttribute": True,
            "attribute_name": "VolumesRW",
            "msg": "R/W volumes mounted in docker.",
            "results": []

        },
        "DOCKER_MOUNTS": {
            "isDockerAttribute": True,
            "attribute_name": "Mounts",
            "msg": "List mounted volumes in docker.",
            "results": []
        }
    }

    for item in driveinfo.keys():
        if driveinfo[item]['isDockerAttribute']:
            option_result = utils.get_value_from_str_dotted_key(
                docker_inspect_output,
                driveinfo[item]['attribute_name']
            )
            del driveinfo[item]['attribute_name']

            # Key not found
            if option_result is None:
                del driveinfo[item]['isDockerAttribute']
                continue
            elif isinstance(option_result, list):
                driveinfo[item]['results'].extend(option_result)
            else:
                driveinfo[item]['results'].append(option_result)

        else:
            cmd = driveinfo[item]['cmd']
            output = container.exec_run(cmd).output.decode('utf-8')
            result = output.split('\n')
            driveinfo[item]['results'] = result
            del driveinfo[item]['cmd']

        del driveinfo[item]['isDockerAttribute']

    result = driveinfo

    res[container.short_id] = {
        _plugin_name_: result
    }

    _log.info('Completed execution of {} Plugin.'.format(_plugin_name_))
    output_queue.put(res)

    if audit:
        # Perform Audit for this result
        _audit(container, driveinfo, audit_queue)


def _audit(container, scan_report, audit_queue):
    """Perform Scan audit.

    :param scan_report: dict
    :param audit_queue: Multiprocessing queue to perform Audit.
    """
    weak_configurations = {
        "MOUNT": {
            'weak_conf': ['rw'],
            'warn_msg': 'READ-WRITE Mount'
        },
        "FSTAB": {
            'weak_conf': ['rw'],
            'warn_msg': 'READ-WRITE mount in fstab'
        },
        "RW_VOLUMES": {
            'weak_conf': ['rw'],
            'warn_msg': 'READ-WRITE Volume'
        },
        "DOCKER_MOUNTS": {
            'weak_conf': ['RW'],
            'warn_msg': 'RW in Docker Mount'
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
