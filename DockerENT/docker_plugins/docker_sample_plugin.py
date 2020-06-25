def scan(container, output_queue):
    """

    :param container: Container to process data for.
    :param output_queue: Output holder for this plugin.

    :return: This plugin returns the object in this form.
    {
        'docker_nw_short_id': object
    }
    """

    res = {}

    res[container.short_id] = {
        __name__ : 'All good'
    }

    output_queue.put(res)
