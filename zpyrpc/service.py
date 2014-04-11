"""A PyZMQ based RPC service.

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

import logging
import sys
import traceback

import zmq
from zmq.eventloop.zmqstream import ZMQStream
from zmq.eventloop.ioloop import IOLoop
from zmq.utils import jsonapi

from .serializer import PickleSerializer


#-----------------------------------------------------------------------------
# RPC Service
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
        self.socket.bind(url)
        self.urls.append(url)

    def bind_ports(self, ip, ports):
        """Try to bind a socket to the first available tcp port.

        The ports argument can either be an integer valued port
        or a list of ports to try. This attempts the following logic:

        * If ports==0, we bind to a random port.
        * If ports > 0, we bind to port.
        * If ports is a list, we bind to the first free port in that list.

        In all cases we save the eventual url that we bind to.

        This raises zmq.ZMQBindError if no free port can be found.
        """
        if isinstance(ports, int):
            ports = [ports]
        for p in ports:
            try:
                if p==0:
                    port = self.socket.bind_to_random_port("tcp://%s" % ip)
                else:
                    self.socket.bind("tcp://%s:%i" % (ip, p))
                    port = p
            except zmq.ZMQError:
                # bind raises this if the port is not free
                continue
            except zmq.ZMQBindError:
                # bind_to_random_port raises this if no port could be found
                continue
            else:
                break
        else:
            raise zmq.ZMQBindError('Could not find an available port')
        url = 'tcp://%s:%i' % (ip, port)
        self.urls.append(url)
        return port

    def connect(self, url):
        """Connect the service to a url of the form proto://ip:port."""
        self.socket.connect(url)
        self.urls.append(url)

class RPCService(RPCBase):
    """An RPC service that takes requests over a ROUTER socket."""

    def _create_socket(self):
        self.socket = self.context.socket(zmq.ROUTER)
        self.stream = ZMQStream(self.socket, self.loop)
        self.stream.on_recv(self._handle_request)

    def _build_reply(self, status, data):
        """Build a reply message for status and data.

        Parameters
        ----------
        status : bytes
            Either b'SUCCESS' or b'FAILURE'.
        data : list of bytes
            A list of data frame to be appended to the message.
        """
        reply = []
        reply.extend(self.idents)
        reply.extend([b'|', self.msg_id, status])
        reply.extend(data)
        return reply

    def _handle_request(self, msg_list):
        """Handle an incoming request.

        The request is received as a multipart message:

        [<idents>, b'|', msg_id, method, <sequence of serialized args/kwargs>]

        The reply depends on if the call was successful or not:

        [<idents>, b'|', msg_id, 'SUCCESS', <sequece of serialized result>]
        [<idents>, b'|', msg_id, 'FAILURE', <JSON dict of ename, evalue, traceback>]

        Here the (ename, evalue, traceback) are utf-8 encoded unicode.
        """
        i = msg_list.index(b'|')
        self.idents = msg_list[0:i]
        self.msg_id = msg_list[i+1]
        method = msg_list[i+2].decode('utf-8')
        data = msg_list[i+3:]
        args, kwargs = self._serializer.deserialize_args_kwargs(data)

        # Find and call the actual handler for message.
        handler = getattr(self, method, None)
        if handler is not None and getattr(handler, 'is_rpc_method', False):
            try:
                result = handler(*args, **kwargs)
            except Exception:
                self._send_error()
            else:
                try:
                    data_list = self._serializer.serialize_result(result)
                except Exception:
                    self._send_error()
                else:
                    reply = self._build_reply(b'SUCCESS', data_list)
                    self.stream.send_multipart(reply)
        else:
            logging.error('Unknown RPC method: %s' % method)
        self.idents = None
        self.msg_id = None

    def _send_error(self):
        """Send an error reply."""
        etype, evalue, tb = sys.exc_info()
        error_dict = {
            'ename' : str(etype.__name__),
            'evalue' : str(evalue),
            'traceback' : traceback.format_exc()
        }
        data_list = [jsonapi.dumps(error_dict)]
        reply = self._build_reply(b'FAILURE', data_list)
        self.stream.send_multipart(reply)

    def start(self):
        """Start the event loop for this RPC service."""
        self.loop.start()


def rpc_method(f):
    """A decorator for use in declaring a method as an rpc method.

    Use as follows::

        @rpc_method
        def echo(self, s):
            return s
    """
    f.is_rpc_method = True
    return f
