"""Main Script for the scanner."""
import logging

import coloredlogs

from DockerENT import controller, config_parser

logger_config = config_parser.config['logger']
logging.config.dictConfig(logger_config)
coloredlogs.install(level='DEBUG')

controller.main()
