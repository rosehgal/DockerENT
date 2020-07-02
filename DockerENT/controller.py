#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import logging
import multiprocessing

from multiprocessing import pool

from DockerENT import scanner_workers

# Define module-level logger.
_log = logging.getLogger(__name__)


def main():
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

    args = parser.parse_args()

    process_count = args.process_count

    docker_containers = args.docker_container
    docker_plugins = args.docker_plugins

    docker_nws = args.docker_network
    docker_nw_plugins = args.docker_nw_plugins

    _log.info('Starting application ...')

    _log.info('Creating application pool space with count {}'
              .format(process_count))

    process_pool = pool.Pool(process_count)
    output_q = multiprocessing.Manager().Queue()

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

    report = {}
    while not output_q.empty():
        result = output_q.get()
        for key in result.keys():
            if key in report.keys():
                report[key].append(result[key])
            else:
                report[key] = []
                report[key].append(result[key])

    if report:
        _log.info(json.dumps(report, indent=2))
