# -*- coding: UTF-8 -*-
from decimal import Decimal
from inspect import isgenerator
import sys

import pytest

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

from py4j import protocol, binary_protocol as bprotocol
from py4j import java_gateway
from py4j import compat


VERSION_INFO = sys.version_info
IS_PYTHON_2 = VERSION_INFO[0] == 2
IS_PYTHON_3 = VERSION_INFO[0] == 3


def test_none_encoder():
    encoder = bprotocol.NoneEncoder()

    value = None
    encoded = encoder.encode(value, type(value))
    assert encoded.type == bprotocol.NULL_TYPE
    assert encoded.size is None
    assert encoded.value is None


def test_int_encoder():
    encoder = bprotocol.IntEncoder()
    value = "Hello"

    assert encoder.encode(value, type(value)) == bprotocol.CANNOT_ENCODE

    value = 1
    encoded = encoder.encode(value, type(value))

    assert encoded.type == bprotocol.INTEGER_TYPE
    assert encoded.size is None
    assert len(encoded.value) == 4

    value = -3000000000000
    encoded = encoder.encode_specific(value, type(value))
    assert encoded.type == bprotocol.LONG_TYPE
    assert encoded.size is None
    assert len(encoded.value) == 8


def test_decimal_encoder():
    encoder = bprotocol.DecimalEncoder()
    value = Decimal("34.56")
    value_str = compat.unicode("34.56").encode("utf-8")

    encoded = encoder.encode(value, type(value))
    assert encoded.type == bprotocol.DECIMAL_TYPE
    assert encoded.size == len(value_str)
    assert len(encoded.value) == len(value_str)


def test_bool_encoder():
    encoder = bprotocol.BoolEncoder()

    value = True
    encoded = encoder.encode(value, type(value))
    assert encoded.type == bprotocol.BOOLEAN_TRUE_TYPE
    assert encoded.size is None
    assert encoded.value is None

    value = False
    encoded = encoder.encode(value, type(value))
    assert encoded.type == bprotocol.BOOLEAN_FALSE_TYPE
    assert encoded.size is None
    assert encoded.value is None


def test_double_encoder():
    encoder = bprotocol.DoubleEncoder()

    def assert_float(value):
        encoded = encoder.encode(value, type(value))
        assert encoded.type == bprotocol.DOUBLE_TYPE
        assert encoded.size is None
        assert len(encoded.value) == 8

    assert_float(2.3)
    assert_float(float("nan"))
    assert_float(float("+inf"))
    assert_float(float("-inf"))


def test_bytes_encoder():
    encoder = bprotocol.BytesEncoder()

    def assert_bytes(value):
        encoded = encoder.encode(value, type(value))
        assert encoded.type == bprotocol.BYTES_TYPE
        assert encoded.size == len(value)
        assert len(encoded.value) == len(value)

    assert_bytes(bytearray([1, 2, 3]))

    value_bytestr = compat.tobytestr("hello")
    if IS_PYTHON_3:
        assert_bytes(value_bytestr)
    else:
        assert encoder.encode(value_bytestr, type(value_bytestr)) ==\
            bprotocol.CANNOT_ENCODE


def test_string_encoder():
    encoder = bprotocol.StringEncoder()

    def assert_string(value):
        bin_string = bprotocol.get_encoded_string(value, "utf-8")
        encoded = encoder.encode(value, type(value))
        assert encoded.type == bprotocol.STRING_TYPE
        assert encoded.size == len(bin_string)
        assert len(encoded.value) == len(bin_string)

    assert_string(compat.unicode("testing\ntesting"))

    value_bytestr = compat.tobytestr("testing\ntesting")
    if IS_PYTHON_2:
        assert_string(value_bytestr)
    else:
        assert encoder.encode(value_bytestr, type(value_bytestr)) ==\
            bprotocol.CANNOT_ENCODE


def test_python_proxy_long_encoder():
    encoder = bprotocol.PythonProxyLongEncoder()

    obj = object()
    value = PythonJavaClass()
    pool = java_gateway.PythonProxyPool()
    suffix = bprotocol.get_encoded_string(
        "com.package.Foo;com.package.Bar", "utf-8")

    assert encoder.encode(obj, type(obj)) == bprotocol.CANNOT_ENCODE

    encoded = encoder.encode(value, type(value), python_proxy_pool=pool)
    assert encoded.type == bprotocol.PYTHON_REFERENCE_TYPE
    assert encoded.size == 8 + len(suffix)
    assert len(encoded.value) == 8 + len(suffix)


def test_exception_encoder():
    registry = bprotocol.EncoderRegistry.get_default_encoder_registry()
    pool = java_gateway.PythonProxyPool()
    try:
        raise ValueError("Hello")
    except Exception as e:
        (_, _, tb) = sys.exc_info()
        error = e
        compat.add_traceback(e, tb)

    encoded_arg = registry.encode(error, python_proxy_pool=pool)
    assert encoded_arg.type == bprotocol.EXCEPTION_TYPE


def test_java_object_long_encoder():
    encoder = bprotocol.JavaObjectLongEncoder()

    java_object = Mock()
    java_object._get_object_id.return_value = 1

    encoded_value = encoder.encode(java_object, java_gateway.JavaObject)
    assert encoded_value.type == bprotocol.JAVA_REFERENCE_TYPE
    assert encoded_value.size is None
    assert len(encoded_value.value) == 8

    encoded_value = encoder.encode_specific(
        java_object, java_gateway.JavaObject)
    assert encoded_value.type == bprotocol.JAVA_REFERENCE_TYPE
    assert encoded_value.size is None
    assert len(encoded_value.value) == 8

    assert encoder.encode(object(), object) == bprotocol.CANNOT_ENCODE


def test_java_class_encoder():
    encoder = bprotocol.JavaClassEncoder()
    java_class = Mock()
    java_class._fqn = "java.util.Random"
    bin_string = bprotocol.get_encoded_string(java_class._fqn, "utf-8")

    encoded_value = encoder.encode(java_class, java_gateway.JavaClass)
    assert encoded_value.type == bprotocol.JAVA_CLASS_TYPE
    assert encoded_value.size == len(bin_string)
    assert encoded_value.value == bin_string

    encoded_value = encoder.encode_specific(
        java_class, java_gateway.JavaClass)
    assert encoded_value.type == bprotocol.JAVA_CLASS_TYPE
    assert encoded_value.size == len(bin_string)
    assert encoded_value.value == bin_string


def test_encoder_registry_encode_error():
    registry = bprotocol.EncoderRegistry.get_default_encoder_registry()

    with pytest.raises(protocol.Py4JProtocolError):
        registry.encode(object())


def test_encoder_registry_basic():
    registry = bprotocol.EncoderRegistry.get_default_encoder_registry()
    registry.add_python_collection_encoders()
    pool = java_gateway.PythonProxyPool()
    java_object = Mock()
    java_object._get_object_id.return_value = 1

    # Test encode specifics
    encoded = registry.encode(1)
    assert encoded.type == bprotocol.INTEGER_TYPE

    encoded = registry.encode(1000000000000)
    assert encoded.type == bprotocol.LONG_TYPE

    encoded = registry.encode("hello world")
    assert encoded.type == bprotocol.STRING_TYPE

    encoded = registry.encode(bytearray([1, 2, 3]))
    assert encoded.type == bprotocol.BYTES_TYPE

    # Test encode
    encoded = registry.encode(FakeStr("hello world"))
    assert encoded.type == bprotocol.STRING_TYPE

    encoded = registry.encode(PythonJavaClass(), python_proxy_pool=pool)
    assert encoded.type == bprotocol.PYTHON_REFERENCE_TYPE

    encoded = registry.encode(java_object)
    assert encoded.type == bprotocol.JAVA_REFERENCE_TYPE


def test_encoder_registry_command():
    registry = bprotocol.EncoderRegistry.get_default_encoder_registry()
    pool = java_gateway.PythonProxyPool()
    java_object = Mock()
    java_object._get_object_id.return_value = 1
    encoded_command = registry.encode_command(
        bprotocol.CALL_COMMAND,
        java_object, "testing", PythonJavaClass(),
        bprotocol.END_ENCODED_ARGUMENT,
        python_proxy_pool=pool)
    # command + 3 args + END
    assert len(encoded_command) == 5


def test_encoder_registry_command_with_collections():
    registry = bprotocol.EncoderRegistry.get_default_encoder_registry()
    registry.add_python_collection_encoders()
    pool = java_gateway.PythonProxyPool()
    java_object = Mock()
    java_object._get_object_id.return_value = 1

    # JavaClass Mocking
    ArrayListInstanceMock = Mock()
    ArrayListInstanceMock._get_object_id.return_value = 1
    ArrayListMock = Mock(return_value=ArrayListInstanceMock)
    JavaClassMock = Mock(return_value=ArrayListMock)

    with patch("py4j.java_collections.JavaClass", new=JavaClassMock):
        encoded_command = registry.encode_command(
            bprotocol.CALL_COMMAND,
            java_object, "testing", PythonJavaClass(), ["1", "2", 3],
            python_proxy_pool=pool, java_client=Mock())
        # command + 4 args
        assert len(encoded_command) == 5


def test_encoder_registry_lazy_command():
    registry = bprotocol.EncoderRegistry.get_default_encoder_registry()
    pool = java_gateway.PythonProxyPool()
    java_object = Mock()
    java_object._get_object_id.return_value = 1
    encoded_command = registry.encode_command_lazy(
        bprotocol.CALL_COMMAND,
        java_object, "testing", PythonJavaClass(),
        python_proxy_pool=pool)

    assert isgenerator(encoded_command)
    encoded_command_list = list(encoded_command)

    # command + 3 args
    assert len(encoded_command_list) == 4


def test_send_encoded_command_basic():
    registry = bprotocol.EncoderRegistry.get_default_encoder_registry()
    pool = java_gateway.PythonProxyPool()
    java_object = Mock()
    java_object._get_object_id.return_value = 1
    encoded_command = registry.encode_command_lazy(
        bprotocol.CALL_COMMAND,
        java_object, u"testingé", PythonJavaClass(),
        python_proxy_pool=pool)
    buffer = bytearray()

    def mock_sendall(payload):
        buffer.extend(payload)

    sock = Mock()
    sock.sendall = mock_sendall

    bprotocol.send_encoded_command(encoded_command, sock)

    # CALL_COMMAND = 2 + 2
    # Java Object = 2 + 8
    # String: 2 + 4 + 9
    # Python Java Class: 2 + 4 + (8 + 31)
    assert len(buffer) == 74


def test_send_encoded_command_small_buff():
    registry = bprotocol.EncoderRegistry.get_default_encoder_registry()
    pool = java_gateway.PythonProxyPool()
    java_object = Mock()
    java_object._get_object_id.return_value = 1
    encoded_command = registry.encode_command_lazy(
        bprotocol.CALL_COMMAND,
        java_object, u"testingé", PythonJavaClass(),
        python_proxy_pool=pool)
    buffer = bytearray()

    def mock_sendall(payload):
        buffer.extend(payload)

    sock = Mock()
    sock.sendall = mock_sendall

    io_mock = Mock()
    io_mock.DEFAULT_BUFFER_SIZE = 8

    with patch("py4j.binary_protocol.io", new=io_mock):
        bprotocol.send_encoded_command(encoded_command, sock)

    # CALL_COMMAND = 2 + 2
    # Java Object = 2 + 8
    # String: 2 + 4 + 9
    # Python Java Class: 2 + 4 + (8 + 31)
    assert len(buffer) == 74


class PythonJavaClass(object):

    class Java:
        implements = ["com.package.Foo", "com.package.Bar"]


class FakeStr(compat.unicode):
    pass
