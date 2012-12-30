"""A base class for RPC services and proxies.

Authors:

* Brian Granger
"""

#-----------------------------------------------------------------------------
#  Copyright (C) 2012. Brian Granger, Min Ragan-Kelley  
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file COPYING.BSD, distributed as part of this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------


import zmq
from zmq.eventloop.ioloop import IOLoop

from .serializer import PickleSerializer

#-----------------------------------------------------------------------------
# RPC base class
#-----------------------------------------------------------------------------


class RPCBase(object):

    def __init__(self, loop=None, context=None, serializer=None):
        """Base class for RPC service and proxy.

        Parameters
        ==========
        loop : IOLoop
            An existing IOLoop instance, if not passed, then IOLoop.instance()
            will be used.
        context : Context
            An existing Context instance, if not passed, the Context.instance()
            will be used.
        serializer : Serializer
            An instance of a Serializer subclass that will be used to serialize
            and deserialize args, kwargs and the result.
        """
        self.loop = loop if loop is not None else IOLoop.instance()
        self.context = context if context is not None else zmq.Context.instance()
        self.socket = None
        self.stream = None
        self._serializer = serializer if serializer is not None else PickleSerializer()
        self.reset()

    #-------------------------------------------------------------------------
    # Public API
    #-------------------------------------------------------------------------

    def reset(self):
        """Reset the socket/stream."""
        if isinstance(self.socket, zmq.Socket):
            self.socket.close()
        self._create_socket()
        self.urls = []

    def bind(self, url):
        """Bind the service to a url of the form proto://ip:port."""
        self.urls.append(url)
        self.socket.bind(url)

    def connect(self, url):
        """Connect the service to a url of the form proto://ip:port."""
        self.urls.append(url)
        self.socket.connect(url)

