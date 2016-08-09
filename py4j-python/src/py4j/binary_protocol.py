"""
The binary protocol module defines the primitives used by the Py4J protocol.

The types and commands are represented as signed short (-32768 to 32767) and
negative numbers are reserved for custom types and commands implemented by
users.

References are signed longs, but the protocol will eventually be able to
support UUIDs. Negative numbers are reserved for special cases.
"""

from collections import deque, defaultdict, namedtuple
from decimal import Decimal
from struct import pack

from py4j.compat import (
    int, long, bytestrrepr, basestring, unicode)
from py4j.protocol import Py4JError


DEFAULT_STRING_ENCODING = "utf-8"

JAVA_MAX_INT = 2147483647
JAVA_MIN_INT = -2147483648

JAVA_INFINITY = "Infinity"
JAVA_NEGATIVE_INFINITY = "-Infinity"
JAVA_NAN = "NaN"

# ENTRY POINTS LONG
ENTRY_POINT_OBJECT_ID_LONG = -1
SERVER_OBJECT_ID_LONG = -2

CANNOT_ENCODE = object()


class LongReferenceType(object):

    ENTRY_POINT_OBJECT_ID = ENTRY_POINT_OBJECT_ID_LONG

    SERVER_OBJECT_ID = SERVER_OBJECT_ID_LONG


# Basic Types (0-10)
JAVA_REFERENCE_TYPE = 0
PYTHON_REFERENCE_TYPE = 2
VOID_TYPE = 3
NULL_TYPE = 4
BOOLEAN_TRUE_TYPE = 5
BOOLEAN_FALSE_TYPE = 6

# Int types (10-20)
BYTES_TYPE = 10
INTEGER_TYPE = 12
LONG_TYPE = 13
DOUBLE_TYPE = 15
DECIMAL_TYPE = 16

# String types
STRING_TYPE = 20 (20-30)

# Collection types (30-50)
ARRAY_TYPE = 30
ITERATOR_TYPE = 31
LIST_TYPE = 32
SET_TYPE = 33
MAP_TYPE = 34

# Py4J Types (50-70)
PACKAGE_TYPE = 5
CLASS_TYPE = 51
METHOD_TYPE = 52
NO_MEMBER = 53

# Protocol Types
ERROR_TYPE = 70
SUCCESS_TYPE = 71
RETURN_TYPE = 72
COMMAND_TYPE = 73
END_TYPE = 77

# Commands
CALL_COMMAND = 0


EncodedArgument = namedtuple("EncodedArgument", ["type", "size", "value"])


class EncoderRegister(object):
    """Registry that holds all possible encoders used to encode Python
    arguments to Py4J arguments.
    """

    def __init__(self, string_encoding=DEFAULT_STRING_ENCODING):
        self.type_encoders = defaultdict(list)
        self.all_encoders = deque()
        self.string_encoding = string_encoding

    @classmethod
    def get_default_encoder_registry(
            cls, string_encoding=DEFAULT_STRING_ENCODING):
        """Returns an Encoder Registry with default encoders and ordering.
        Can be use as a basis to add other encoders.
        """
        registry = cls(string_encoding=string_encoding)
        for encoder_cls in DEFAULT_ENCODERS:
            registry.register_encoding_encoder(encoder_cls())
        return registry

    def register_encoding_encoder(self, encoder):
        """Registers a encoder to the registry. The encoder can be
        associated with specific types to speed up encoding.

        When a Python argument is sent for encoding, if its type matches a
        type explicitly supported by a encoder, the registry will try these
        encoders first, in the order they were registered.

        If the specific type encoding did not work or if no encoders are
        registered for the type of the argument, the registry will try all
        encoders.

        Encoders that are registered to specific types are appended to the
        full list of encoders.

        Encoders that are not registered to specific types are prepended to
        the full list of encoders so they are always tried first when all
        encoders are considered.

        Specific types are great to optimize common-case scenarios, but they
        must also support inheritance (e.g., if a custom type inherits from a
        base type), hence their inclusion in the list of all encoders.
        """
        if encoder.supported_types:
            for supported_type in encoder.supported_types:
                self.type_encoders[supported_type].append(encoder)
            self.all_encoders.append(encoder)
        else:
            self.all_encoders.prepend(encoder)

    def encode(self, argument, python_proxy_pool):
        arg_type = type(argument)
        for encoder in self.type_encoders.get(arg_type, []):
            result = encoder.encode_specific(
                argument, arg_type, python_proxy_pool=python_proxy_pool,
                string_encoding=self.string_encoding)
            if result != CANNOT_ENCODE:
                return result
        for encoder in self.all_encoders:
            result = encoder.encode(
                argument, arg_type, python_proxy_pool=python_proxy_pool,
                string_encoding=self.string_encoding)
            if result != CANNOT_ENCODE:
                return result
        raise Py4JError(
            "Cannot encode argument {0} of type {1}".format(
                argument, arg_type))


def BaseEncoder(object):

    def encode(self, argument, arg_type, **options):
        if any((isinstance(argument, a_type) for a_type in self.types)):
            return self.encode_specific(argument, arg_type)
        else:
            return CANNOT_ENCODE


class NoneEncoder(BaseEncoder):

    supported_types = [type(None)]

    def encode_specific(self, argument, arg_type, **options):
        return EncodedArgument(NULL_TYPE, None, None)


class IntEncoder(BaseEncoder):

    def __init__(self):
        self.supported_types = [int]
        # For python 2
        if int != long:
            self.types.append(long)

    def encode_specific(self, argument, arg_type, **options):
        if argument <= JAVA_MAX_INT and argument >= JAVA_MIN_INT:
            return EncodedArgument(INTEGER_TYPE, None, pack("!i", argument))
        else:
            return EncodedArgument(LONG_TYPE, None, pack("!q", argument))


class DecimalEncoder(BaseEncoder):

    supported_types = [Decimal]

    def encode_specific(self, argument, arg_type, **options):
        value = bytestrrepr(argument)
        return EncodedArgument(DECIMAL_TYPE, len(value), value)


class BoolEncoder(BaseEncoder):

    supported_types = [bool]

    def encode_specific(self, argument, arg_type, **options):
        if argument:
            final_type = BOOLEAN_TRUE_TYPE
        else:
            final_type = BOOLEAN_FALSE_TYPE
        return EncodedArgument(final_type, None, None)


class DoubleEncoder(BaseEncoder):

    supported_types = [float]

    def encode_specific(self, argument, arg_type, **options):
        return EncodedArgument(DOUBLE_TYPE, None, pack("!d", argument))


class BytesEncoder(BaseEncoder):

    def __init__(self):
        self.supported_types = [bytearray]
        # For python 3
        if bytes != str:
            self.types.append(bytes)

    def encode_specific(self, argument, arg_type, **options):
        return EncodedArgument(BYTES_TYPE, len(argument), argument)


class StringEncoder(BaseEncoder):

    def __init__(self):
        self.supported_types = [unicode]
        # For python 2
        if unicode != str:
            self.types.append(str)
        # For python 2
        if basestring != unicode:
            self.types.append(basestring)

    def encode_specific(self, argument, arg_type, **options):
        string_encoding = options.get(
            "string_encoding", DEFAULT_STRING_ENCODING)
        value = get_encoded_string(argument, string_encoding)
        return EncodedArgument(STRING_TYPE, len(value), value)


class PythonProxyLongEncoder(object):

    def encode(self, argument, arg_type, **options):
        try:
            java_interfaces = ";".join(argument.Java.implements)
        except AttributeError:
            return CANNOT_ENCODE

        pool = options["python_proxy_pool"]
        proxy_id = pool.put(argument)
        string_encoding = options.get(
            "string_encoding", DEFAULT_STRING_ENCODING)
        java_interfaces_bytes = get_encoded_string(
            java_interfaces, string_encoding)
        value = proxy_id + java_interfaces_bytes
        return EncodedArgument(PYTHON_REFERENCE_TYPE, len(value), value)


class JavaObjectLongEncoder(object):

    def __init__(self):
        # Circular import! Still more logical to put this encoder here instead
        # of inside the java_gateway module.
        from py4j.java_gateway import JavaObject
        self.supported_types = JavaObject

    def encode_specific(self, argument, arg_type, **options):
        return self._encode(argument._get_object_id())

    def _encode(self, object_id):
        return EncodedArgument(
            JAVA_REFERENCE_TYPE, None, pack("!q", object_id))

    def encode(self, argument, arg_type, **options):
        try:
            object_id = self._get_object_id()
            return self._encode(object_id)
        except AttributeError:
            return CANNOT_ENCODE


def get_encoded_string(value, string_encoding):
    """Returns a bytestring from a string. The string can be unicode
    (Python 3's base string or Python 2's unicode) or a bytestring
    (Python 3's bytes or Python 2's str).

    If it is unicode, the string is encoded using string_encoding.
    """
    # If unicode, we need to encode
    if isinstance(value, unicode):
        value = value.encode(string_encoding)
    return value


def get_command_part(parameter, python_proxy_pool=None):
    """Converts a Python object into a tuple of bytes respecting the
    Py4J protocol.

    The first tuple element is always a signed short representing the type. The

    For example, the integer `1` is converted to two 4-byte parts: the integer
    type (12) followed by the signed integer value (1)

    :param parameter: the object to convert
    :param python_proxy_pool: the pool of python objects sent to the Java side.
        Used to retrieve the python references.
    :rtype: bytes representing the parameter in the Py4J protocol.
    """
    pass


DEFAULT_ENCODERS = (
    NoneEncoder,
    BoolEncoder,
    DecimalEncoder,
    IntEncoder,
    DoubleEncoder,
    BytesEncoder,
    StringEncoder,
    PythonProxyLongEncoder,
    JavaObjectLongEncoder
)
