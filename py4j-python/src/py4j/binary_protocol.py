"""
The binary protocol module defines the primitives used by the Py4J protocol.

The types and commands are represented as signed short (-32768 to 32767) and
negative numbers are reserved for custom types and commands implemented by
users.

References are signed longs, but the protocol will eventually be able to
support UUIDs. Negative numbers are reserved for special cases.
"""

from collections import deque, defaultdict, namedtuple, Sequence
from decimal import Decimal
from struct import pack

from py4j.compat import (
    long, bytestrrepr, basestring, unicode)
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

# String types (20-30)
STRING_TYPE = 20

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

# Python types that dpend on Python 2 and 3 differences

SUPPORTED_STRING_TYPES = [unicode]
# For python 2
if unicode != str:
    SUPPORTED_STRING_TYPES.append(str)
# For python 2
if basestring != unicode:
    SUPPORTED_STRING_TYPES.append(basestring)

SUPPORTED_BYTE_TYPES = [bytearray]
# For python 3
if bytes != str:
    SUPPORTED_BYTE_TYPES.append(bytes)

SUPPORTED_INT_TYPES = [int]
# For python 2
if int != long:
    SUPPORTED_INT_TYPES.append(long)


EncodedArgument = namedtuple("EncodedArgument", ["type", "size", "value"])


class EncoderRegistry(object):
    """Registry that holds all possible encoders used to encode Python
    arguments to Py4J arguments.

    This class is not thread-safe: if multiple thread tries to register
    encoders at the same time, concurrent modification errors may be raised.

    Multiple threads can call the encode method though if they are not
    registering encoders at the same time.
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

    def add_python_collection_encoders(self):
        """Adds converters that copies the elements of a Python collection into
        a Java collection. Both collections are not synchronized, i.e., a
        change on the Java side is not reflected on the Python side.
        """
        from py4j.java_collections import (
            PythonListEncoder, PythonMapEncoder, PythonSetEncoder)
        self.register_encoding_encoder(PythonListEncoder())
        self.register_encoding_encoder(PythonMapEncoder())
        self.register_encoding_encoder(PythonSetEncoder())

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
            self.all_encoders.appendleft(encoder)

    def encode_command(
            self, commands, arguments=None, java_client=None,
            python_proxy_pool=None):
        commands = force_sequence(commands)
        encoded_arguments = []
        for command in commands:
            encoded_arguments.append(
                EncodedArgument(COMMAND_TYPE, None, command))
        for argument in arguments:
            encoded_arguments.append(
                self.encode(argument, java_client=java_client,
                            python_proxy_pool=python_proxy_pool))
        return encoded_arguments

    def encode_lazy_command(
            self, commands, arguments=None, java_client=None,
            python_proxy_pool=None):
        commands = force_sequence(commands)
        for command in commands:
            yield EncodedArgument(COMMAND_TYPE, None, command)

        for argument in arguments:
            yield self.encode(
                argument, java_client=java_client,
                python_proxy_pool=python_proxy_pool)

    def encode(self, argument, java_client=None, python_proxy_pool=None):
        arg_type = type(argument)
        for encoder in self.type_encoders.get(arg_type, []):
            result = encoder.encode_specific(
                argument, arg_type,
                java_client=java_client,
                python_proxy_pool=python_proxy_pool,
                string_encoding=self.string_encoding)
            if result != CANNOT_ENCODE:
                return result
        for encoder in self.all_encoders:
            result = encoder.encode(
                argument, arg_type,
                java_client=java_client,
                python_proxy_pool=python_proxy_pool,
                string_encoding=self.string_encoding)
            if result != CANNOT_ENCODE:
                return result
        raise Py4JError(
            "Cannot encode argument {0} of type {1}".format(
                argument, arg_type))


class BaseEncoder(object):

    def encode(self, argument, arg_type, **options):
        if any((isinstance(argument, a_type) for
                a_type in self.supported_types)):
            return self.encode_specific(argument, arg_type)
        else:
            return CANNOT_ENCODE


class NoneEncoder(BaseEncoder):

    supported_types = [type(None)]

    def encode_specific(self, argument, arg_type, **options):
        return EncodedArgument(NULL_TYPE, None, None)


class IntEncoder(BaseEncoder):

    supported_types = SUPPORTED_INT_TYPES

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

    supported_types = SUPPORTED_BYTE_TYPES

    def encode_specific(self, argument, arg_type, **options):
        return EncodedArgument(BYTES_TYPE, len(argument), argument)


class StringEncoder(BaseEncoder):

    supported_types = SUPPORTED_STRING_TYPES

    def encode_specific(self, argument, arg_type, **options):
        string_encoding = options.get(
            "string_encoding", DEFAULT_STRING_ENCODING)
        value = get_encoded_string(argument, string_encoding)
        return EncodedArgument(STRING_TYPE, len(value), value)


class PythonProxyLongEncoder(object):

    supported_types = []

    def encode(self, argument, arg_type, **options):
        try:
            java_interfaces = ";".join(argument.Java.implements)
        except AttributeError:
            return CANNOT_ENCODE

        pool = options["python_proxy_pool"]
        proxy_id = pack("!q", pool.put(argument))
        string_encoding = options.get(
            "string_encoding", DEFAULT_STRING_ENCODING)
        java_interfaces_bytes = get_encoded_string(
            java_interfaces, string_encoding)
        value = proxy_id + java_interfaces_bytes
        return EncodedArgument(PYTHON_REFERENCE_TYPE, len(value), value)


class JavaObjectLongEncoder(object):

    supported_types = []

    def __init__(self):
        # Circular import! Still more logical to put this encoder here instead
        # of inside the java_gateway module.
        from py4j.java_gateway import JavaObject
        self.supported_types = JavaObject

    def encode_specific(self, argument, arg_type, **options):
        return self.encode_java_object(argument._get_object_id())

    @classmethod
    def encode_java_object(cls, object_id):
        return EncodedArgument(
            JAVA_REFERENCE_TYPE, None, pack("!q", object_id))

    def encode(self, argument, arg_type, **options):
        try:
            object_id = self._get_object_id()
            return self.encode_java_object(object_id)
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


def force_sequence(value):
    """Convert a value to a sequence if it is a string or a non-sequence.
    """
    if isinstance(value, basestring):
        return [value]
    elif not isinstance(value, Sequence):
        return [value]
    else:
        return value


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
