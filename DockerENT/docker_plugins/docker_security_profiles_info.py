"""Docker security profiles scan plugin."""
from DockerENT.utils import utils

import docker
import logging

_log = logging.getLogger(__name__)

_plugin_name_ = 'security-profiles'


def scan(container, output_queue, audit=False, audit_queue=None):
    """Docker security profiles scan plugin.

    This plugin inspect the AppArmor and SELinux profile for running
    container via low level docker python sdk low level api.

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

    security_options = {
        "AppArmor_Profile": {
            "output_identifier": "AppArmorProfile",
            "msg": "AppArmor Profile options.",
            "results": []
        },
        "SELinux": {
            "output_identifier": "HostConfig.SecurityOpt",
            "msg": "SELinux security options.",
            "results": []
        },
        "CapAdd": {
            "output_identifier": "HostConfig.CapAdd",
            "msg": "A list of kernel capabilities to added to the container.",
            "results": []
        },
        "CapDrop": {
            "output_identifier": "HostConfig.CapDrop",
            "msg": "A list of kernel capabilities to drop from the container.",
            "results": []
        },
        "Capabilities": {
            "output_identifier": "HostConfig.Capabilities",
            "msg": "A list of kernel capabilities present container.",
            "results": []
        },
        "Privileged": {
            "output_identifier": "HostConfig.Privileged",
            "msg": " Gives the container full access to the host.",
            "results": []
        },

    }

    for option in security_options.keys():
        option_result = utils.get_value_from_str_dotted_key(
            docker_inspect_output,
            security_options[option]['output_identifier']
        )
        if isinstance(option_result, list):
            security_options[option]['results'] = option_result
        elif option_result is None:
            security_options[option]['results'] = [None]
        else:
            security_options[option]['results'].append(option_result)

        del security_options[option]['output_identifier']

    res[container.short_id] = {
        _plugin_name_: security_options
    }

    _log.info('Completed execution of {} Plugin.'.format(_plugin_name_))
    output_queue.put(res)

    if audit:
        # Perform Audit for this result
        _audit(container, security_options, audit_queue)


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
        'AppArmor_Profile': {
            'weak_conf': ['', None, '<no value>', 'unconfined'],
            'warn_msg': 'No AppArmorProfile Found'
        },
        'SELinux': {
            'weak_conf': ['', None, '<no value>', 'unconfined',
                          'label=disable'],
            'warn_msg': 'SELinux disabled'
        },
        'CapAdd': {
            'safe_conf': [],
            'warn_msg': 'Capabilities Present: '
        },
        'Privileged': {
            'weak_conf': ['true', 'TRUE', True],
            'warn_msg': 'Container is Privileged'
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
