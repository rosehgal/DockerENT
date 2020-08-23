"""UI for DockerENT"""
import pkgutil

from docker.models import plugins

import DockerENT.scanner_workers

import multiprocessing

import streamlit as st
import docker

from DockerENT import scanner_workers

sidebar = st.sidebar

st.title("This is DockerENT")

docker_client = docker.from_env()

docker_list = docker_client.containers.list()
docker_list = [docker_name.short_id for docker_name in docker_list]
docker_list.insert(0, 'all')

docker_nw_list = docker_client.networks.list()
docker_nw_list.insert(0, 'all')

scan_dockers = sidebar.checkbox('Scan dockers')
scan_docker_networks = sidebar.checkbox('Scan docker networks')

start_scan = None
progress_bar = None
process_count = None
docker_scan_plugins = None
dockers_to_scan = None
docker_scan_options = None

if scan_dockers:
    docker_scan_options = sidebar.selectbox(
        'Pick a single docker or all to start.',
        docker_list
    )

    _plugins = ['all']
    for importer, modname, ispkg in pkgutil.iter_modules(
            DockerENT.docker_plugins.__path__):
        _plugins.append(str(modname))

    docker_scan_plugins = sidebar.multiselect(
        'Select the list of plugins to execute',
        _plugins
    )

if scan_docker_networks:
    docker_nw_options = sidebar.selectbox(
        'Pick a single network or all to start',
        docker_nw_list
    )

if scan_dockers or scan_docker_networks:
    start_scan = sidebar.button('Start Scan')
    process_count = sidebar.slider("Number of processes", 1, 10, 2, 1)

dockers_to_scan = [docker_scan_options]
print(dockers_to_scan)

if start_scan:
    # To start the scan, setup process poll and output queue
    # Create process pool
    output_q = multiprocessing.Manager().Queue()
    st.text('Starting scan ...')

    _containers = []
    if dockers_to_scan == 'all' or dockers_to_scan[0] == 'all':
        _containers = docker_client.containers.list()
    else:
        _containers.append(docker_client.containers.get(docker_scan_options))
    print(_containers)

    _plugins = []

    if docker_scan_plugins is None or docker_scan_plugins == 'all' \
            or docker_scan_plugins[0] == 'all':
        for importer, modname, ispkg in pkgutil.iter_modules(
                DockerENT.docker_plugins.__path__):
            _plugins.append(modname)
    else:
        _plugins.append(docker_scan_plugins)
    print(_plugins)

    for container in _containers:
        for plugin in _plugins:
            scanner_workers.executor(
                target=container.short_id,
                plugin=plugin,
                output_queue=output_q,
                is_docker=True
            )

    st.write(output_q)
    report = {}

    while not output_q.empty():
        result = output_q.get()
        for key in result.keys():
            if key in report.keys():
                report[key].append(result[key])
            else:
                report[key] = []
                report[key].append(result[key])
    st.write(report)
