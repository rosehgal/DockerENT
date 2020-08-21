"""UI for DockerENT"""
import pkgutil
import DockerENT.scanner_workers

import multiprocessing
from multiprocessing import pool

import streamlit as st
import docker

from DockerENT import scanner_workers, output_worker

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

if scan_dockers:
    docker_scan_options = sidebar.selectbox(
        'Pick a single docker or all to start.',
        docker_list
    )

    _plugins = []
    for importer, modname, ispkg in pkgutil.iter_modules(
            DockerENT.docker_plugins.__path__):
        _plugins.append(modname)

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

if start_scan:
    # To start the scan, setup process poll and output queue
    # Create process pool
    process_pool = pool.Pool(process_count)
    output_q = multiprocessing.Manager().Queue()
    st.text('Starting scan ...')

    st.write(docker_scan_plugins)

    scanner_workers.docker_scan_worker(
        containers=docker_scan_options,
        plugins=docker_scan_plugins,
        process_pool=process_pool,
        output_queue=output_q
    )

    process_pool.close()
    process_pool.join()

    st.write(output_q)
    report = {}

    while not output_q.empty():
        result = output_q.get()
        st.write(result)
        for key in result.keys():
            if key in report.keys():
                report[key].append(result[key])
            else:
                report[key] = []
                report[key].append(result[key])

    output_worker.output_handler(queue=output_q, target='file')
