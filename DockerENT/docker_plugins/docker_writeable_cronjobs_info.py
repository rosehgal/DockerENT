"""Docker cron jobs scan plugin."""
import logging

_log = logging.getLogger(__name__)

_plugin_name_ = 'cron-info'


def scan(container, output_queue, audit=False, audit_queue=None):
    """Docker cron-jobs scan plugin.

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
