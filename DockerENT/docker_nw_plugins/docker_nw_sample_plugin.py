"""Docker network sample scan plugin."""
import logging

_log = logging.getLogger(__name__)

_plugin_name_ = 'sample_nw'


def scan(container, output_queue, audit=False, audit_queue=None):
    """Docker sample_nw scan plugin.

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
    _log.info('Staring {} Plugin ...'.format(_plugin_name_))

    res = {

    }
    result = {
        'test_performed': {
            'results': ['good']
        }
    }

    # do some processing.
    # Since this is sample plugin there is no processing.

    res[container.short_id] = {
        _plugin_name_: result
    }
    _log.info('Completed execution of {} Plugin.'.format(_plugin_name_))

    output_queue.put(res)
