"""Config & Config parser for DockerENT."""
import yaml

config_yml = """
logger:
  version: 1
  disable_existing_loggers: false
  formatters:
    simple:
      format: >-
          %(asctime)s [%(process)s] [%(processName)s] [%(threadName)s]
          %(levelname)s %(name)s:%(lineno)d - %(message)s
      datefmt: "%Y-%m-%d %H:%M:%S"
  handlers:
    rich_console:
      class: rich.logging.RichHandler
      formatter: simple
    console:
      class: logging.StreamHandler
      formatter: simple
      stream: ext://sys.stdout
  loggers:
    adal-python:
      level: WARNING
  root:
    level: INFO
    handlers:
      - rich_console
"""
config = yaml.safe_load(config_yml)
