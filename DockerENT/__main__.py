"""Main Script for the scanner."""
import logging
import logging.config

from DockerENT import controller, config_parser

# Setup config for this package
logger_config = config_parser.config['logger']
logging.config.dictConfig(logger_config)

# Start the scanner
controller.main()
