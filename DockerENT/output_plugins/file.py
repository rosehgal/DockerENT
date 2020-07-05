"""File output plugin.

Process the records and write the content to the file as plain json.
"""
import json
import logging

_log = logging.getLogger(__name__)

_plugin_name_ = 'file-output-plugin'


def write(queue, filename='out.json'):
    """Write report to to file.

    :param queue: The input queue which contains the data from various scan
        plugins.
    :type queue: multiprocessing.managers.AutoProxy[Queue]

    :param filename: Name of file to output to.
    :type filename: str

    :return: None
    """
    _log.info("Writing to file {} ...".format(filename))

    # Perform data massaging
    report = {}
    while not queue.empty():
        result = queue.get()
        for key in result.keys():
            if key in report.keys():
                report[key].append(result[key])
            else:
                report[key] = []
                report[key].append(result[key])

    if report:
        with open(filename, 'w+') as file:
            file.write(json.dumps(report, indent=2))

    _log.info("Written to disk {}".format(filename))
