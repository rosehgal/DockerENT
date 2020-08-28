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

        if type(option_result) == type(list):
            security_options[option]['results'].extend(option_result)
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
    """Perform Scan audit

    :param scan_report: dict
    :param audit_queue: Multiprocessing queue to perform Audit.
    """
    container_id = container.short_id
    audit_report = {}
    audit_report[container_id] = []

    weak_configurations = ['', None, '<no value>', 'unconfined']
    for security_option in scan_report.keys():
        actual_results = scan_report[security_option]['results']

        if [] in actual_results:
            actual_results.remove([])
            actual_results.append(None)

        if (set(actual_results) & set(weak_configurations)) != set():
            # Weak configuration detected
            audit_report[container_id].append(
                'Weak '+security_option
            )

    audit_queue.put(audit_report)
