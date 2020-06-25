"""

"""
import importlib
import logging
import pkgutil

import docker

import DockerENT
from DockerENT import docker_plugins
from DockerENT import docker_nw_plugins

_log = logging.getLogger(__name__)

docker_client = docker.from_env()


def executor(target, plugin, output_queue, is_docker=False):
    """

    :param target:
    :param plugin: Plugin to execute
    :param is_docker:

    :return: None
    """

    # load the plugin module
    if is_docker:
        package = docker_plugins.__package__
        target = docker_client.containers.get(target)
    else:
        package = docker_nw_plugins.__package__
        target = docker_client.networks.get(target)

    module = importlib.import_module(package + '.' + plugin)
    module.scan(target, output_queue)


def docker_scan_worker(containers, plugins, process_pool, output_queue):
    """

    :param output_queue:
    :param containers: List of docker containers to test for.
    :type containers: list[docker.models.containers.Container]
    :param plugins: List of plugins to operate for.
    :param process_pool: The multiprocessing pool object.

    :return: None
    """
    _containers = []
    if containers is None or containers == 'all':
        _containers = docker_client.containers.list()
    else:
        _containers.append(docker_client.containers.get(containers))

    _plugins = []
    if plugins is None or plugins == 'all':
        for importer, modname, ispkg in pkgutil.iter_modules(
                DockerENT.docker_plugins.__path__):
            _plugins.append(modname)
    else:
        _plugins.append(plugins)

    plugins = _plugins
    containers = _containers

    _log.info('{} docker plugin(s) loaded ...'.format(
        len(plugins)))

    _log.info('{} docker containers loaded ...'.format(len(containers)))

    executor_args = []
    for container in containers:
        for plugin in plugins:
            executor_args.append((container.id, plugin, output_queue, True,))

    _log.debug(executor_args)

    process_pool.starmap_async(executor, executor_args)


def docker_nw_scan_worker(nws, plugins, process_pool, output_queue):
    """

    :param output_queue:
    :param nws: List of docker nws to test for.
    :type nws: list[docker.models.networks.Network]
    :param plugins: List of plugins to operate for.
    :param process_pool: The multiprocessing pool object.

    :return: None
    """
    _nws = []
    if nws is None or nws == 'all':
        _nws = docker_client.networks.list()
    else:
        _nws.append(docker_client.networks.get(nws))

    _plugins = []
    if plugins is None or plugins == 'all':
        for importer, modname, ispkg in pkgutil.iter_modules(
                DockerENT.docker_nw_plugins.__path__):
            _plugins.append(modname)
    else:
        _plugins.append(plugins)

    plugins = _plugins
    nws = _nws

    _log.info('{} docker-network plugin(s) loaded ...'.format(
        len(plugins)))

    _log.info('{} docker containers loaded ...'.format(len(nws)))

    executor_args = []
    for nw in nws:
        for plugin in plugins:
            executor_args.append((nw.id, plugin, output_queue, False,))

    _log.debug(executor_args)

    process_pool.starmap_async(executor, executor_args)
