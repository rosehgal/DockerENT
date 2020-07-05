"""Helper functions goes here."""

import copy


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
