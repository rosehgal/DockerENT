import logging

_log = logging.getLogger(__name__)

_plugin_name_ = 'cron-info'


def scan(container, output_queue):
    """Plugin to perform checks on cron jobs.

    :param container: Container to process data for.
    :param output_queue: Output holder for this plugin.

    :return: This plugin returns the object in this form.
    {
        _plugin_name_: object
    }
    """

    res = {}

    _log.info('Staring {} Plugin ...'.format(_plugin_name_))

    croninfo = {
        "user-cron-jobs": {
            "cmd": "crontab -l 2>/dev/null",
            "msg": "Users cron jobs",
            "results": []
        }
    }

    for item in croninfo:
        cmd = croninfo[item]['cmd']
        output = container.exec_run(cmd).output.decode('utf-8')
        result = output.split('\n')
        croninfo[item]['results'] = result
        del croninfo[item]['cmd']

    result = croninfo

    res[container.short_id] = {
        _plugin_name_: result
    }

    _log.info('Completed execution of {} Plugin.'.format(_plugin_name_))
    output_queue.put(res)
