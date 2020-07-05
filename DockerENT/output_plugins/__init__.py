"""The package for output plugins packaged with this project.

This package contains output plugins which are packaged with this project.
The output plugins implements a function ``write`` that accepts the queue of
type multiprocessing.managers.AutoProxy[Queue] and process the elements from
the queue and create output pipeline.
"""
