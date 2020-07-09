"""Audit worker, defines how to audit response from each plugin."""
import logging

_log = logging.getLogger(__name__)


def audit(input_queue, output_queue):
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
    :param input_queue: This queue holds the output from each plugin executed.
    :type input_queue: multiprocessing.managers.AutoProxy[Queue]

    :param output_queue: This queue holds the output from each plugin executed.
    :type output_queue: multiprocessing.managers.AutoProxy[Queue]

    :return: None
    """
    while not input_queue.empty():
        result = input_queue.get()
        _log.info(result)
        output_queue.put(result)
