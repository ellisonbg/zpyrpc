"""A simple but fast RPC library for Python using ZeroMQ.

Authors:

* Brian Granger

Example
-------

To create a simple service::

    from zpyrpc import RPCService
    class Echo(RPCService):

        @rpc_method
        def echo(self, s):
            return s

    echo = Echo()
    echo.bind('tcp://127.0.0.1:5555')
    IOLoop.instance().start()

To talk to this service::

    from zpyrpc import RPCServiceProxy
    p = RPCServiceProxy()
    p.connect('tcp://127.0.0.1:5555')
    p.echo('Hi there')
    'Hi there'
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

from .service import RPCService, rpc_method
from .proxy import (
    AsyncRPCServiceProxy, RPCServiceProxy,
    AsyncRemoteMethod, RemoteMethod, 
    RPCError, RemoteRPCError, RPCTimeoutError
)
from .serializer import *

