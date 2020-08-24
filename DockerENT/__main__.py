"""Main Script for DockerENT.

Script will load any config file and make it available to application.
"""
from DockerENT import config_parser
from DockerENT import controller

import logging.config
import argparse
import subprocess
import os
import sys

# Setup config for this package
logger_config = config_parser.config['logger']
logging.config.dictConfig(logger_config)

# Read arguments for DockerENT application
parser = argparse.ArgumentParser(
    prog='Find the vulnerabilities hidden in your running container(s).'
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
    default=False
)

parser.add_argument(
    '-n',
    '--process',
    nargs='?',
    dest='process_count',
    default=2,
    type=int,
    help='Run scans in parallel.'
)

parser.add_argument(
    '-a',
    '--audit',
    dest='audit',
    action='store_true',
    default=False
)

output_plugin = parser.add_argument_group()
output_plugin.add_argument(
    '-o',
    '--output',
    nargs='?',
    dest='output',
    default='file',
    type=str,
    help='Output plugin to write data to'
)

args = parser.parse_args()

process_count = args.process_count
output = args.output
audit = args.audit
webapp = args.web_app

docker_containers = args.docker_container
docker_plugins = args.docker_plugins

docker_nws = args.docker_network
docker_nw_plugins = args.docker_nw_plugins

# Start DockerENT
# If webapp, start Streamlit else cli application.
if webapp:
    sys.path.append(os.path.abspath(os.path.join('..')))
    web_app_cmd = "streamlit run web_app.py"
    subprocess.run(web_app_cmd.split(" "), stdout=subprocess.PIPE)
else:
    controller.main(docker_containers=docker_containers,
                    docker_plugins=docker_plugins,
                    docker_nws=docker_nws,
                    docker_nw_plugins=docker_nw_plugins,
                    process_count=process_count,
                    audit=audit,
                    output=output)
