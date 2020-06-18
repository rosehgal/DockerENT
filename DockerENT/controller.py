#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging

# Define module-level logger.
_log = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        prog='Find the vulnerabilities hidden in your running container(s).'
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-d',
        '--docker',
        nargs='?',
        dest='docker_name',
        const='all',
        help='Run scan against the running container.')
    group.add_argument(
        '-d-nw',
        '--docker-network',
        nargs='?',
        dest='docker_network_name',
        const='all',
        help='Run scan against running docker-network')

    args = parser.parse_args()

    _log.info('Starting application ...')

    if args.docker_name:
        if args.docker_name == 'all':
            # scan all docker images
            pass
        else:
            # check if image exist and start scanner
            pass

    elif args.docker_network_name:
        if args.docker_network_name == 'all':
            # scan all docker images
            pass
        else:
            # check if image exist and start scanner
            pass
    else:
        print("None is present")
