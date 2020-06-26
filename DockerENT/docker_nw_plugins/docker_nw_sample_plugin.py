import logging

_log = logging.getLogger(__name__)

_plugin_name_ = 'sample_nw'


def scan(container, output_queue):
    """

    :param container: Container to process data for.
    :param output_queue: Output holder for this plugin.

    :return: This plugin returns the object in this form.
    {
        'docker_nw_sample_plugin': object
    }
    """

    _log.info('Staring {} Plugin ...'.format(_plugin_name_))

    res = {

    }
    result = {
        'status': 'good'
    }

    # do some processing.
    # Since this is sample plugin there is not processing done here.

    res[container.short_id] = {
        _plugin_name_: result
    }

    _log.info('Completed execution of {} Plugin.'.format(_plugin_name_))

    output_queue.put(res)
