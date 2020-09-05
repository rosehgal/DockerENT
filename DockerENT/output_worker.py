"""Output worker, defines how to process output from each plugin."""
import importlib
import logging

_log = logging.getLogger(__name__)


def output_handler(queue, target, filename='out.json'):
    """Worker function passes the queue to target.

    :param queue: This queue holds the output from each plugin executed.
    :type queue: multiprocessing.managers.AutoProxy[Queue]

    :param target: Specifies which output plugin to write data to.
    :type target: DockerENT.output_plugins

    :return: None
    """
    output_plugin = importlib.import_module('DockerENT.output_plugins.'+target)
    output_plugin.write(queue, filename)
