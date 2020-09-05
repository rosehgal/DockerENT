"""Start scanner workers.

This is scanner worker, this will trigger the plugin based scan on docker and
on docker-network which are specified by the controller.
"""
from DockerENT import docker_nw_plugins
from DockerENT import docker_plugins

import docker
import DockerENT
import importlib
import logging
import pkgutil

_log = logging.getLogger(__name__)

docker_client = docker.from_env()


def executor(target,
             plugin,
             output_queue,
             is_docker=False,
             audit=False,
             audit_queue=None):
    """Execute a plugin on the target.

    Target is either a docker.models.containers.Container or
    docker.models.networks.Network.
    The plugin will be either from DockerENT.docker_plugins or
    DockerENT.docker_nw_plugins depending upon the target type.

    :param target: Target to run plugin on.
    :type target: docker.models.containers.Container or
        docker.models.networks.Network

    :param plugin: Plugin.
    :type plugin: DockerENT.docker_plugins or
        DockerENT.docker_nw_plugins

    :param output_queue: Queue to hold output from each plugin.
    :type output_queue: multiprocessing.managers.AutoProxy[Queue]

    :param is_docker: specify is the target is docker or docker-nw instance.
    :type is_docker: bool

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
    module.scan(target, output_queue, audit, audit_queue)


def docker_scan_worker(containers, plugins, process_pool, output_queue,
                       audit, audit_queue):
    """Docker scan worker.

    :param containers: Containers to scan.
    :type containers: List[docker.models.containers.Container]

    :param plugins: List of plugins..
    :type plugins: List[DockerENT.docker_plugins]

    :param process_pool: The multiprocessing pool object.
    :type process_pool: multiprocessing.pool.Pool

    :param output_queue: Queue to hold data from each plugin after execution.
    :type output_queue: multiprocessing.managers.AutoProxy[Queue]

    :return: None
    """
    _containers = []
    if containers == 'all' or containers[0] == 'all':
        _containers = docker_client.containers.list()
    else:
        _containers.append(docker_client.containers.get(containers))
    print(_containers)
    _plugins = []
    if plugins is None or plugins == 'all' or plugins[0] == 'all':
        for importer, modname, ispkg in pkgutil.iter_modules(
                DockerENT.docker_plugins.__path__):
            _plugins.append(modname)
    else:
        _plugins.append(plugins)

    plugins = _plugins
    containers = _containers

    _log.info('{} docker containers loaded ...'.format(len(containers)))
    _log.info('{} docker plugin(s) loaded ...'.format(len(plugins)))

    executor_args = []
    for container in containers:
        for plugin in plugins:
            executor_args.append(
                (container.id, plugin, output_queue, True, audit, audit_queue))

    _log.debug(executor_args)

    process_pool.starmap(executor, executor_args)


def docker_nw_scan_worker(nws, plugins, process_pool, output_queue):
    """Docker Network scan worker.

    :param nws: Docker networks to scan.
    :type nws: List[docker.models.networks.Network]

    :param plugins: List of plugins..
    :type plugins: List[DockerENT.docker_nw_plugins]

    :param process_pool: The multiprocessing pool object.
    :type process_pool: multiprocessing.pool.Pool

    :param output_queue: Queue to hold data from each plugin after execution.
    :type output_queue: multiprocessing.managers.AutoProxy[Queue]

    :return: None
    """
    _nws = []
    if nws == 'all':
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

    _log.info('{} docker nws loaded ...'.format(len(nws)))
    _log.info('{} docker-network plugin(s) loaded ...'.format(
        len(plugins)))

    executor_args = []
    for nw in nws:
        for plugin in plugins:
            executor_args.append((nw.id, plugin, output_queue, False,))

    _log.debug(executor_args)

    process_pool.starmap_async(executor, executor_args)
