"""Serialization classes for ZPyRPC.

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

try:
    import cPickle as pickle
except ImportError:
    import pickle

from zmq.utils import jsonapi


#-----------------------------------------------------------------------------
# Serializer
#-----------------------------------------------------------------------------


class Serializer(object):
    """A class for serializing/deserializing objects."""

    def loads(self, s):
        return pickle.loads(s)

    def dumps(self, o):
        return pickle.dumps(o)

    def serialize_args_kwargs(self, args, kwargs):
        """Serialize args/kwargs into a msg list."""
        return self.dumps(args), self.dumps(kwargs)

    def deserialize_args_kwargs(self, msg_list):
        """Deserialize a msg list into args, kwargs."""
        return self.loads(msg_list[0]), self.loads(msg_list[1])

    def serialize_result(self, result):
        """Serialize a result into a msg list."""
        return [self.dumps(result)]

    def deserialize_result(self, msg_list):
        """Deserialize a msg list into a result."""
        return self.loads(msg_list[0])

PickleSerializer = Serializer

class JSONSerializer(Serializer):
    """A class for serializing using JSON."""

    def loads(self, s):
        return jsonapi.loads(s)

    def dumps(self, o):
        return jsonapi.dumps(o)

