# ZPyRPC = "Zippy RPC"

Zippy fast and simple RPC based on ZeroMQ and Python

## Overview

This library provides a simple, but fast and robust RPC library for
ZeroMQ. It was originally designed in the context of IPython, but
we eventually spun it out into its own project.

Some of the nice features:

* Round robin load balance requests to multiple services.
* Set a timeout on RPC calls.
* Route requests using all of the glory of ZeroMQ.
* Fast, but simple.
* Both synchronous and asynchronous clients/proxies.
* Run multple services in a single process.
* Pluggable serialization (default is pickle, json included).

## Example

To create a simple service:

```
from zpyrpc import RPCService
class Echo(RPCService):

    @rpc_method
    def echo(self, s):
        return s

echo = Echo()
echo.bind('tcp://127.0.0.1:5555')
IOLoop.instance().start()
```

To talk to this service::

```
from zpyrpc import RPCServiceProxy
p = RPCServiceProxy()
p.connect('tcp://127.0.0.1:5555')
p.echo('Hi there')
'Hi there'
```

