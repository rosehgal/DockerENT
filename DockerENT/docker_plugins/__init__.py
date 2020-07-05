"""The package for docker scanner plugins packaged with this project.

This package contains docker-scanner plugins which are packaged with this
project. The docker-scanner plugins implements a function ``scan`` that
accepts a container instance of type ``docker.models.containers.Container``
and a queue of type ``multiprocessing.managers.AutoProxy[Queue]`` and then
executes the ``scan`` on that specific container.

``scan`` function should return a dict of below form for output plugins to work
    {
        _plugin_name_: {
            'test_performed': {
                'results':  []
            }
        }
    }
"""
