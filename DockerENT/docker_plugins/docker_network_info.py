"""Docker network-info scan plugin."""
from DockerENT.utils import utils

import docker
import logging

_log = logging.getLogger(__name__)

_plugin_name_ = 'netinfo'


def scan(container, output_queue, audit=False, audit_queue=None):
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

    api_client = docker.APIClient()
    docker_inspect_output = api_client.inspect_container(container.short_id)

    netinfo = {
        "NETINFO": {
            "isDockerInspectAttribute": False,
            "cmd": "/sbin/ifconfig -a",
            "msg": "Interfaces",
            "results": []
        },
        "ROUTE": {
            "isDockerInspectAttribute": False,
            "cmd": "route",
            "msg": "Route(s)",
            "results": []
        },
        "NETSTAT": {
            "isDockerInspectAttribute": False,
            "cmd": "netstat -antup",
            "msg": "Netstat",
            "results": []
        },
        "PORT_BINDINGS": {
            "isDockerInspectAttribute": True,
            "attribute_name": "NetworkSettings.Ports",
            "msg": "Docker port bindings",
            "results": []
        }
    }

    for item in netinfo.keys():
        if not netinfo[item]['isDockerInspectAttribute']:
            cmd = netinfo[item]['cmd']
            output = container.exec_run(cmd).output.decode('utf-8')
            result = output.split('\n')
            netinfo[item]['results'] = result
            del netinfo[item]['cmd']
        else:
            if netinfo[item]['isDockerInspectAttribute']:
                option_result = utils.get_value_from_str_dotted_key(
                    docker_inspect_output,
                    netinfo[item]['attribute_name']
                )
                del netinfo[item]['attribute_name']

                # Key not found
                if option_result is None:
                    del netinfo[item]['isDockerInspectAttribute']
                    continue
            # Output of docker inspect port is a map, with keys as
            netinfo[item]['results'].append(option_result)

        del netinfo[item]['isDockerInspectAttribute']

    result = netinfo

    res[container.short_id] = {
        _plugin_name_: result
    }

    _log.info('Completed execution of {} Plugin.'.format(_plugin_name_))
    output_queue.put(res)

    if audit:
        _audit(container, netinfo, audit_queue)


def _audit(container, scan_report, audit_queue):
    """Perform Scan audit.

    :param scan_report: dict
    :param audit_queue: Multiprocessing queue to perform Audit.
    """

    container_id = container.short_id
    audit_report = {}
    audit_report[container_id] = []

    columns = [_plugin_name_, 'INFO']

    weak_configurations = {
        'PORT_BINDINGS': {
            'safe_conf': [],
            'warn_msg': 'Port Mapping found:'
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
                    _r = [res for res in actual_results if res]
                    if security_option == 'PORT_BINDINGS':
                        if _r:
                            r = columns + [warn_message + ";".join(
                                utils.docker_network_response_parser(_r)
                            )]
                            audit_report[container_id].append(", ".join(r))
            else:
                if utils.list_intersection(actual_results, weak_results) != []:
                    # Weak configuration detected
                    r = columns + [warn_message]
                    audit_report[container_id].append(
                        ", ".join(r)
                    )

    audit_queue.put(audit_report)
