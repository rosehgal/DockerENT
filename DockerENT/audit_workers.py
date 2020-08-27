"""Audit worker, defines how to audit response from each plugin."""
import logging

_log = logging.getLogger(__name__)

# This is how audit config looks like:
# {
#     'plugin-name': {
#         'plugin-type': 'cis-benchmark/info/offensive',
#         'check-name': {
#             'check-results': [
#              ],
#             'monkey-patch': True/False,
#             'moneky-patch-target': function,
#             'warn-message': 'Warning'
#         }
#     }
# }

audit_config = {
    'security-profiles': {
        'AppArmor_Profile': {
            'check-results': [
                '',
                [],
                '<no value>',
                'unconfined',
                None
            ],
            'monkey-patch': False,
            'monkey-patch-target': None,
            'warn-message': 'No AppArmorProfile Found'
        },
        'SELinux': {
            'check-results': [
                '',
                [],
                '<no value>',
                'unconfined',
                None
            ],
            'monkey-patch': False,
            'monkey-patch-target': None,
            'warn-message': 'No SELinux profile Found'
        }
    }
}


def audit(input):
    """Audit worker function.

    The each element from queue looks like this.
    {
        'container_id': {
            'plugin_name': {
                'check_name': {
                    'msg': 'foo',
                    'results': []
                }
            }
        }
    }
    :param input: This dict holds the output from each plugin executed.
    :type input: dict

    :return: dict
    """
    _log.info('Starting audit worker ...')

    audits_available = audit_config.keys()
    audit_report = {key: {} for key in input.keys()}

    for container_id in input.keys():
        container_results = input[container_id]

        # If there is configuration in audit for input results
        # Evaluate and start audit
        for plugin_name in container_results.keys():
            if plugin_name in audits_available:
                audit_checks = audit_config[plugin_name]

                for scan_name in audit_checks.keys():
                    # Evaluate results
                    if not audit_checks[scan_name]['monkey-patch']:
                        r = []
                        results = container_results[plugin_name][scan_name]['results']

                        for a in audit_checks[scan_name]['check-results']:
                            if a in results:
                                if 'warn' in audit_report[container_id]:
                                    audit_report[container_id]['warn'].append(
                                        audit_checks[scan_name]['warn-message'])
                                else:
                                    audit_report[container_id]['warn'] = []
                                    audit_report[container_id]['warn'].append(
                                        audit_checks[scan_name]['warn-message'])
                    else:
                        # Perform monkey path operation.
                        pass

    _log.info('Audit completed.')
    return audit_report
