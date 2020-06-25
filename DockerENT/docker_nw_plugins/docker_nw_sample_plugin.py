def scan(nw, output_queue):
    """
    :param nw: Docker network to scan
    :param output_queue: The output holder.

    :return: This plugin returns the object in this form.
    {
        'docker_nw_short_id': object
    }
    """

    res = {}
    res[nw.short_id] = {
        __name__: 'All good'
    }

    output_queue.put(res)
