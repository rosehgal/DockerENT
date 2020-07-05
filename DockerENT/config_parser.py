"""Config parser for DockerENT."""

from importlib import resources as pkg_resources

import DockerENT
import yaml

config = yaml.safe_load(pkg_resources.open_text(DockerENT, 'config.yml'))
