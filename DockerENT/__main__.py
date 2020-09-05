"""Main Script for DockerENT.

Script will load any config file and make it available to application.
"""
from DockerENT import config_parser
from DockerENT import controller
import DockerENT

import argparse
import logging.config
import os
import signal
import subprocess
import sys


def start():
    # Setup config for this package
    logger_config = config_parser.config['logger']
    logging.config.dictConfig(logger_config)

    _log = logging.getLogger(__name__)

    # Read arguments for DockerENT application
    parser = argparse.ArgumentParser(
        prog='Find the vulnerabilities hidden in your running container(s).'
    )

    parser.add_argument(
        '-v',
        '--version',
        dest='version',
        action='store_true',
        default=False,
        help='DockerENT version.'
    )

    docker_args_group = parser.add_argument_group()
    docker_args_group.add_argument(
        '-d',
        '--docker',
        nargs='?',
        dest='docker_container',
        const='all',
        help='Run scan against the running container.')
    docker_args_group.add_argument(
        '-p',
        '--plugins',
        nargs='?',
        dest='docker_plugins',
        const='all',
        help='Run scan with only specified plugins.')

    docker_nw_args_group = parser.add_argument_group()
    docker_nw_args_group.add_argument(
        '-d-nw',
        '--docker-network',
        nargs='?',
        dest='docker_network',
        const='all',
        help='Run scan against running docker-network.')
    docker_args_group.add_argument(
        '-p-nw',
        '--nw-plugins',
        nargs='?',
        dest='docker_nw_plugins',
        const='all',
        help='Run scan with only specified plugins.')

    parser.add_argument(
        '-w',
        '--web-app',
        dest='web_app',
        action='store_true',
        default=False,
        help='Run DockerENT in WebApp mode. '
        'If this parameter is enabled, other command line flags will be ignored.'
    )

    parser.add_argument(
        '-n',
        '--process',
        nargs='?',
        dest='process_count',
        default=2,
        type=int,
        help='Run scans in parallel (Process pool count).'
    )

    parser.add_argument(
        '-a',
        '--audit',
        dest='audit',
        action='store_true',
        default=False,
        help='Flag to check weather to audit results or not.'
    )

    output_plugin = parser.add_argument_group()
    output_plugin.add_argument(
        '-o',
        '--output',
        nargs='?',
        dest='output',
        default='file',
        type=str,
        help='Output plugin to write data to.'
    )

    args = parser.parse_args()

    if args.version:
        print(DockerENT.__version__)
        return

    process_count = args.process_count
    output = args.output
    audit = args.audit
    webapp = args.web_app

    docker_containers = args.docker_container
    docker_plugins = args.docker_plugins

    docker_nws = args.docker_network
    docker_nw_plugins = args.docker_nw_plugins

    # Register Signal Handler for graceful exit in case of Web application

    def sigterm_handler(_signo, _stack_frame):
        """Signal handler."""
        _log.info("Thanks for using DockerENT")
        sys.exit(0)

    signal.signal(signal.SIGINT, sigterm_handler)

    # Start DockerENT
    # If webapp, start Streamlit else cli application.
    if webapp:
        _log.info('Starting web application ...')

        sys.path.append(os.path.abspath(os.path.join('.')))
        web_app_cmd = "streamlit run web_app.py"

        with subprocess.Popen(web_app_cmd.split(" ")) as web_process:
            _log.info(web_process.stdout.read())

    else:
        controller.main(docker_containers=docker_containers,
                        docker_plugins=docker_plugins,
                        docker_nws=docker_nws,
                        docker_nw_plugins=docker_nw_plugins,
                        process_count=process_count,
                        audit=audit,
                        output=output)


start()
