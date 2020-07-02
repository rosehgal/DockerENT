import logging
import importlib

_log = logging.getLogger(__name__)


def output_handler(queue, target):
    """This worker function that will write the results to target.

    :param queue: The queue process data from.
    :param target: target to write data to.
    :return:
    """

    output_plugin = importlib.import_module('DockerENT.output_plugins.'+target)
    output_plugin.write(queue)
