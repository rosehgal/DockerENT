"""The controller module, the main method of this module starts DockerENT."""
from DockerENT import audit_workers
from DockerENT import output_worker
from DockerENT import scanner_workers
from multiprocessing import pool

import argparse
import logging
import multiprocessing

# Define module-level logger.
_log = logging.getLogger(__name__)


def main():
    """Start DockerENT application.

    :return: None
    """
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

    docker_containers = args.docker_container
    docker_plugins = args.docker_plugins

    docker_nws = args.docker_network
    docker_nw_plugins = args.docker_nw_plugins

    _log.info('Starting application ...')

    _log.info('Creating application pool space with count {}'
              .format(process_count))

    process_pool = pool.Pool(process_count)
    output_q = multiprocessing.Manager().Queue()
    audit_output_q = multiprocessing.Manager().Queue()

    if docker_containers is not None:
        scanner_workers.docker_scan_worker(
            containers=docker_containers,
            plugins=docker_plugins,
            process_pool=process_pool,
            output_queue=output_q
        )

    if docker_nws is not None:
        scanner_workers.docker_nw_scan_worker(
            nws=docker_nws,
            plugins=docker_nw_plugins,
            process_pool=process_pool,
            output_queue=output_q
        )

    process_pool.close()
    process_pool.join()

    if audit:
        audit_workers.audit(output_q, audit_output_q)
        output_worker.output_handler(queue=audit_output_q, target=output)

    output_worker.output_handler(queue=output_q, target=output)
