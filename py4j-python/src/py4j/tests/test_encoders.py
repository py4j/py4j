from decimal import Decimal
from inspect import isgenerator

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

from py4j import binary_protocol as bprotocol
from py4j import java_gateway
from py4j import compat

import sys

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
    assert encoded.type == bprotocol.PYTHON_REFERENCE_LONG_TYPE
    assert encoded.size == 8 + len(suffix)
    assert len(encoded.value) == 8 + len(suffix)


def test_java_object_long_encoder():
    encoder = bprotocol.JavaObjectLongEncoder()

    java_object = Mock()
    java_object._get_object_id.return_value = 1

    encoded_value = encoder.encode(java_object, java_gateway.JavaObject)
    assert encoded_value.type == bprotocol.JAVA_REFERENCE_LONG_TYPE
    assert encoded_value.size is None
    assert len(encoded_value.value) == 8

    encoded_value = encoder.encode_specific(
        java_object, java_gateway.JavaObject)
    assert encoded_value.type == bprotocol.JAVA_REFERENCE_LONG_TYPE
    assert encoded_value.size is None
    assert len(encoded_value.value) == 8

    assert encoder.encode(object(), object) == bprotocol.CANNOT_ENCODE


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
    assert encoded.type == bprotocol.PYTHON_REFERENCE_LONG_TYPE

    encoded = registry.encode(java_object)
    assert encoded.type == bprotocol.JAVA_REFERENCE_LONG_TYPE


def test_encoder_registry_command():
    registry = bprotocol.EncoderRegistry.get_default_encoder_registry()
    pool = java_gateway.PythonProxyPool()
    java_object = Mock()
    java_object._get_object_id.return_value = 1
    encoded_args = registry.encode_command(
        bprotocol.CALL_COMMAND,
        [java_object, "testing", PythonJavaClass()],
        python_proxy_pool=pool)
    # command + 3 args + END
    assert len(encoded_args) == 5


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
        encoded_args = registry.encode_command(
            bprotocol.CALL_COMMAND,
            [java_object, "testing", PythonJavaClass(), ["1", "2", 3]],
            python_proxy_pool=pool, java_client=Mock())
        # command + 4 args + END
        assert len(encoded_args) == 6


def test_encoder_registry_lazy_command():
    registry = bprotocol.EncoderRegistry.get_default_encoder_registry()
    pool = java_gateway.PythonProxyPool()
    java_object = Mock()
    java_object._get_object_id.return_value = 1
    encoded_args = registry.encode_command_lazy(
        bprotocol.CALL_COMMAND,
        [java_object, "testing", PythonJavaClass()],
        python_proxy_pool=pool)

    assert isgenerator(encoded_args)
    encoded_args_list = list(encoded_args)

    # command + 3 args + END
    assert len(encoded_args_list) == 5


class PythonJavaClass(object):

    class Java:
        implements = ["com.package.Foo", "com.package.Bar"]


class FakeStr(compat.unicode):
    pass
