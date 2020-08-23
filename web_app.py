"""Web App for DockerENT"""
from DockerENT import scanner_workers
from docker.models import plugins
import DockerENT.scanner_workers
import docker
import multiprocessing
import pkgutil
import streamlit as ui

ui_sidebar = ui.sidebar

# Title for Web application. Shown main web app
ui.title("DockerENT")

# Get the docker client to interact with docker api.
docker_client = docker.from_env()

# Get the list of all docker containers for sidebar drop down
docker_list = docker_client.containers.list()

# Convert container objects to string, for use by executor.
docker_list = [docker_name.short_id for docker_name in docker_list]
# Add option for 'all' to be shown in UI
docker_list.insert(0, 'all')

# Get the list of all docker-nw for sidebar drop down
docker_nw_list = docker_client.networks.list()
docker_nw_list.insert(0, 'all')

# --------------------------- SIDEBAR START --------------------------------
# Initialise all UI Sidebar widgets
# Order is preserved in UI
ui_sidebar.text('Select options to start DockerENT')
scan_dockers_checkbox = ui_sidebar.checkbox('Scan dockers')
scan_docker_networks_checkbox = ui_sidebar.checkbox('Scan docker networks')

# Placeholders
docker_list_dropdown = None
docker_plugins_list_dropdown = None
docker_nw_list_dropdown = None
docker_nw_plugin_list_dropdown = None
ui_sidebar_start_docker_scan = None
# --------------------------- SIDEBAR END ----------------------------------


# --------------------------- UI START -------------------------------------
# Initialise all UI widgets
# Order is preserved in UI
ui_progress_bar = None
# --------------------------- UI END ---------------------------------------


# Global UI result variables
docker_scan_list = None
docker_scan_plugins = None


class AutoUpdateProgressBar:
    def __init__(self, iterable, progress_bar):
        self.prog_bar = progress_bar
        self.iterable = iterable
        self.length = len(iterable)
        self.i = 0

    def __iter__(self):
        for obj in self.iterable:
            yield obj
            self.i += 1
            current_prog = self.i / self.length
            self.prog_bar.progress(current_prog)


def render_sidebar():
    global docker_scan_list
    global docker_scan_plugins

    if scan_dockers_checkbox:
        docker_scan_list = ui_sidebar.selectbox(
            label='Pick a single docker or all to start.',
            options=docker_list
        )

        _plugins = ['all']
        for importer, modname, ispkg in pkgutil.iter_modules(
                DockerENT.docker_plugins.__path__):
            _plugins.append(modname)

        docker_scan_plugins = ui_sidebar.multiselect(
            'Select the list of plugins to execute',
            _plugins
        )

        ui_sidebar_docker_start_scan = ui_sidebar.button(
            'Start docker scan'
        )

    if ui_sidebar_docker_start_scan:
        scan_dockers()


def render_ui():
    pass


def scan_dockers():
    global docker_scan_list
    global docker_scan_plugins

    # Create a Q to handle report from each plugin
    output_q = multiprocessing.Manager().Queue()

    _containers = []
    if docker_scan_list == 'all' or docker_scan_list[0] == 'all':
        _containers = docker_client.containers.list()
    else:
        _containers.append(docker_client.containers.get(docker_scan_list))

    _plugins = []

    if docker_scan_plugins is None or docker_scan_plugins == 'all' \
            or docker_scan_plugins[0] == 'all':
        for importer, modname, ispkg in pkgutil.iter_modules(
                DockerENT.docker_plugins.__path__):
            _plugins.append(modname)
    else:
        _plugins = docker_scan_plugins

    docker_scan_progress_bar = ui.progress(0)
    # List of Tuples(target, plugin)to hold target to plugin combinations
    target_plugin = []

    for container in _containers:
        for plugin in _plugins:
            target_plugin.append((container, plugin))

    with ui.spinner('Scanning dockers ..'):
        for i in AutoUpdateProgressBar(range(len(target_plugin)), docker_scan_progress_bar):
            scanner_workers.executor(
                target=target_plugin[i][0].short_id,
                plugin=target_plugin[i][1],
                output_queue=output_q,
                is_docker=True
            )
    ui.success('Scan Complete')

    report = {}
    while not output_q.empty():
        result = output_q.get()
        for key in result.keys():
            if key in report.keys():
                report[key].append(result[key])
            else:
                report[key] = []
                report[key].append(result[key])

    ui.json(report)


def scan_docker_networks():
    pass


def main():
    render_sidebar()


main()
