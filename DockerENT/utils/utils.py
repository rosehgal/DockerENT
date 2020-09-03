"""Helper functions goes here."""

import copy


def parse_output_queue_2_dict(output_q):
    """Utility function to parse the output queue to python dict."""
    report = {}
    while not output_q.empty():
        result = output_q.get()
        for key in result.keys():
            if key in report.keys():
                report[key].update(result[key])
            else:
                report[key] = {}
                report[key].update(result[key])

    return report


def parse_audit_queue_2_dict(audit_q):
    """Utility function to parse the audit queue to python dict."""
    audit_report = {}
    while not audit_q.empty():
        result = audit_q.get()
        for key in result.keys():
            if not key in audit_report.keys():
                audit_report[key] = []

            audit_report[key].extend(result[key])
    return audit_report


def get_value_from_str_dotted_key(d, dotted_key):
    """Get value from python dict via dotted notation.

    :param d: dictionary
    :param dotted_key:

    :return: str
    """
    keys = dotted_key.split('.')
    temp = copy.deepcopy(d)
    try:
        for key in keys:
            temp = temp[key]
        return temp
    except KeyError:
        return None


def list_intersection(lst1, lst2):
    """List intersection."""
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


def docker_network_response_parser(port_mapping_list):
    """Parse list to source - dest port.

    Input:
        [
            {
                '8080/tcp': [{'HostIp': '0.0.0.0', 'HostPort': '80'}],
                '90/tcp': [{'HostIp': '0.0.0.0', 'HostPort': '9090'}]
            }
        ]

    Output:
        ["HostIp(0.0.0.0):HostPort(80):GuestPort(8080)"]
    """
    result = []
    port_map = port_mapping_list[0]
    for pm in port_map.keys():
        result.append(
            "HostIp("+port_map[pm][0]['HostIp'] +
            "):HostPort("+port_map[pm][0]['HostPort'] +
            "):GuestPort("+pm+")"
        )
    return result
