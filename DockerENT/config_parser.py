import yaml
import importlib.resources as pkg_resources

import DockerENT

config = yaml.safe_load(pkg_resources.open_text(DockerENT, 'config.yml'))
