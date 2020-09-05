"""The controller module, the main method of this module starts DockerENT."""
from DockerENT import output_worker
from DockerENT import scanner_workers
from multiprocessing import pool

import logging
import multiprocessing

# Define module-level logger.
_log = logging.getLogger(__name__)


def main(docker_containers,
         docker_plugins,
         docker_nws,
         docker_nw_plugins,
         process_count,
         audit,
         output):
    """Start DockerENT application.

    :return: None
    """
    _log.info('Starting application ...')

    _log.info('Creating application pool space with count {}'
              .format(process_count))

    process_pool = pool.Pool(process_count)
    output_q = multiprocessing.Manager().Queue()
    audit_q = None

    if audit:
        audit_q = multiprocessing.Manager().Queue()

    if docker_containers is not None:
        scanner_workers.docker_scan_worker(
            containers=docker_containers,
            plugins=docker_plugins,
            process_pool=process_pool,
            output_queue=output_q,
            audit=audit,
            audit_queue=audit_q
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

    output_worker.output_handler(
        queue=output_q,
        target=output)

    if audit:
        output_worker.output_handler(
            queue=audit_q,
            target=output,
            filename='audit.json'
        )
