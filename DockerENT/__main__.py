"""Main Script for DockerENT.

Script will load any config file and make it available to application.
"""
from DockerENT import config_parser
from DockerENT import controller

import logging.config

# Setup config for this package
logger_config = config_parser.config['logger']
logging.config.dictConfig(logger_config)

# Start DockerENT
controller.main()
