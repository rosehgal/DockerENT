"""The package for docker-nw scanner plugins packaged with this project.

This package contains docker-nw-scanner plugins which are packaged with this
project. The docker-nw-scanner plugins implements a function ``scan`` that
accepts a nw instance of type ``docker.models.networks.Network``
and a queue of type ``multiprocessing.managers.AutoProxy[Queue]`` and then
executes the ``scan`` on that specific nw.

``scan`` function should return a dict of below form for output plugins to work
    {
        _plugin_name_: {
            'test_performed': {
                'results':  []
            }
        }
    }
"""
