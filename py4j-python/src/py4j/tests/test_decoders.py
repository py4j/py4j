# -*- coding: UTF-8 -*-
from decimal import Decimal
from io import BytesIO
from math import isnan
from struct import pack

import pytest

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

from py4j import protocol, binary_protocol as bprotocol


def test_none_decoder():
    decoder = bprotocol.SingleTypeDecoder()
    b = BytesIO(bytes())
    assert decoder.decode(b, bprotocol.NULL_TYPE) is None


def test_int_decoder():
    decoder = bprotocol.IntDecoder()
    b = BytesIO(pack("!i", 23))
    assert decoder.decode(b, bprotocol.INTEGER_TYPE) == 23

    b = BytesIO(pack("!q", 23))
    assert decoder.decode(b, bprotocol.LONG_TYPE) == 23


def test_decimal_decoder():
    decoder = bprotocol.DecimalDecoder()
    bin_s = b"1.23"
    size = len(bin_s)
    b = BytesIO(pack("!i", size) + bin_s)
    value = decoder.decode(b, bprotocol.DECIMAL_TYPE)
    assert value == Decimal("1.23")


def test_double_decoder():
    decoder = bprotocol.DoubleDecoder()
    b = BytesIO(pack("!d", 1.23))
    value = decoder.decode(b, bprotocol.DOUBLE_TYPE)

    assert round(value - 1.23, 5) == 0

    decoder = bprotocol.DoubleDecoder()
    b = BytesIO(pack("!d", float("nan")))
    value = decoder.decode(b, bprotocol.DOUBLE_TYPE)

    assert isnan(value)

    decoder = bprotocol.DoubleDecoder()
    b = BytesIO(pack("!d", float("+inf")))
    value = decoder.decode(b, bprotocol.DOUBLE_TYPE)

    assert float("+inf") == value

    decoder = bprotocol.DoubleDecoder()
    b = BytesIO(pack("!d", float("-inf")))
    value = decoder.decode(b, bprotocol.DOUBLE_TYPE)

    assert float("-inf") == value


def test_bool_decoder():
    decoder = bprotocol.BoolDecoder()
    b = BytesIO(bytes())

    assert decoder.decode(b, bprotocol.BOOLEAN_TRUE_TYPE) is True
    assert decoder.decode(b, bprotocol.BOOLEAN_FALSE_TYPE) is False


def test_string_decoder():
    decoder = bprotocol.StringDecoder()
    s = u"hello world éééé"
    bin_s = bprotocol.get_encoded_string(s, "utf-8")
    size = len(bin_s)
    b = BytesIO(pack("!i", size) + bin_s)
    value = decoder.decode(b, bprotocol.STRING_TYPE)
    assert value == s


def test_bytes_decoder():
    decoder = bprotocol.BytesDecoder()
    bin_s = b"Hello world"
    size = len(bin_s)

    b = BytesIO(pack("!i", size) + bin_s)
    value = decoder.decode(b, bprotocol.BYTES_TYPE)
    assert value == bin_s


def test_python_proxy_long_decoder():
    decoder = bprotocol.PythonProxyLongDecoder()
    pool = {45: object()}
    b = BytesIO(pack("!q", 45))
    python_instance = decoder.decode(
        b, bprotocol.PYTHON_REFERENCE_TYPE, python_proxy_pool=pool)

    assert python_instance == pool[45]


def test_java_object_long_decoder():
    with patch("py4j.java_gateway.JavaObject") as java_object_mock:
        decoder = bprotocol.JavaObjectLongDecoder()
        java_client = Mock()
        b = BytesIO(pack("!q", 45))
        java_object = decoder.decode(
            b, bprotocol.JAVA_REFERENCE_TYPE, java_client=java_client)

        assert java_object is not None
        java_object_mock.assert_called_once_with(
            45, java_client)


def test_error_with_exception_decoder():
    with patch("py4j.java_gateway.JavaObject") as java_object_mock:
        registry = bprotocol.DecoderRegistry.get_default_decoder_registry()
        java_client = Mock()
        b = BytesIO(
            pack("!h", bprotocol.EXCEPTION_TYPE) +
            pack("!q", 45)
        )
        decoded_argument = registry.decode_argument(
            b, java_client=java_client)

        assert decoded_argument.type == bprotocol.EXCEPTION_TYPE
        assert decoded_argument.value is not None

        java_object_mock.assert_called_once_with(
            45, java_client)

        assert registry.is_error_argument(decoded_argument)


def test_java_collection_long_decoder():
    with patch("py4j.java_gateway.JavaObject") as java_object_mock:
        decoder = bprotocol.JavaObjectLongDecoder()
        java_client = Mock()
        b = BytesIO(pack("!q", 45))
        java_object = decoder.decode(
            b, bprotocol.MAP_TYPE, java_client=java_client)

        assert java_object is not None
        java_object_mock.assert_called_once_with(
            45, java_client)


def test_java_class_decoder():
    with patch("py4j.java_gateway.JavaClass") as java_class_mock:
        decoder = bprotocol.JavaClassDecoder()
        java_client = Mock()
        bin_s = bprotocol.get_encoded_string("java.util.Random", "utf-8")
        size = len(bin_s)
        b = BytesIO(pack("!i", size) + bin_s)
        java_class = decoder.decode(
            b, bprotocol.JAVA_CLASS_TYPE, java_client=java_client)

        assert java_class is not None
        java_class_mock.assert_called_once_with(
            "java.util.Random", java_client)


def test_decoder_registry_already_registered():
    registry = bprotocol.DecoderRegistry.get_default_decoder_registry()
    with pytest.raises(protocol.Py4JError):
        registry.register_decoder(bprotocol.SingleTypeDecoder())

    registry.register_decoder(bprotocol.SingleTypeDecoder(), force=True)


def test_decoder_registry_bad_type():
    registry = bprotocol.DecoderRegistry.get_default_decoder_registry()
    b = BytesIO(
        pack("!h", -25) +
        pack("!i", 23))
    with pytest.raises(protocol.Py4JProtocolError):
        registry.decode_argument(b)


def test_decoder_registry_decode_argument_basic():
    registry = bprotocol.DecoderRegistry.get_default_decoder_registry()

    s = u"helloé"
    bin_s = bprotocol.get_encoded_string(s, "utf-8")
    size = len(bin_s)

    b = BytesIO(
        pack("!h", bprotocol.STRING_TYPE) +
        pack("!i", size) +
        bin_s +
        pack("!h", bprotocol.INTEGER_TYPE) +
        pack("!i", 23))

    arg1 = registry.decode_argument(b)
    arg2 = registry.decode_argument(b)

    assert arg1 == bprotocol.DecodedArgument(
        bprotocol.STRING_TYPE, s)
    assert arg2 == bprotocol.DecodedArgument(
        bprotocol.INTEGER_TYPE, 23)


def test_decoder_registry_decode_arguments_basic():
    registry = bprotocol.DecoderRegistry.get_default_decoder_registry()

    s = u"helloé"
    bin_s = bprotocol.get_encoded_string(s, "utf-8")
    size = len(bin_s)

    b = BytesIO(
        pack("!h", bprotocol.STRING_TYPE) +
        pack("!i", size) +
        bin_s +
        pack("!h", bprotocol.BOOLEAN_TRUE_TYPE) +
        pack("!h", bprotocol.NULL_TYPE) +
        pack("!h", bprotocol.END_TYPE)
    )

    args = registry.decode_arguments(b)

    assert 3 == len(args)
    assert args[0] == bprotocol.DecodedArgument(
        bprotocol.STRING_TYPE, s)
    assert args[1] == bprotocol.DecodedArgument(
        bprotocol.BOOLEAN_TRUE_TYPE, True)
    assert args[2] == bprotocol.DecodedArgument(
        bprotocol.NULL_TYPE, None)


def test_get_return_value():
    registry = bprotocol.DecoderRegistry.get_default_decoder_registry()

    assert registry.get_return_value(
        bprotocol.DecodedArgument(bprotocol.VOID_TYPE, None)) is None

    assert 11 == registry.get_return_value(
        bprotocol.DecodedArgument(bprotocol.INTEGER_TYPE, 11))

    with pytest.raises(protocol.Py4JJavaError):
        registry.get_return_value(
            bprotocol.DecodedArgument(
                bprotocol.EXCEPTION_TYPE, Mock()), 123, "foo")

    with pytest.raises(protocol.Py4JError):
        registry.get_return_value(
            bprotocol.DecodedArgument(
                bprotocol.ERROR_TYPE, None), 123, "foo")

    with pytest.raises(protocol.Py4JError):
        registry.get_return_value(
            bprotocol.DecodedArgument(
                bprotocol.ERROR_TYPE, None))


def test_decoder_registry_java_collections():
    registry = bprotocol.DecoderRegistry.get_default_decoder_registry()
    registry.add_java_collection_decoders()

    b = BytesIO(
        pack("!h", bprotocol.ITERATOR_TYPE) +
        pack("!q", 3) +
        pack("!h", bprotocol.MAP_TYPE) +
        pack("!i", 4) +
        pack("!h", bprotocol.LIST_TYPE) +
        pack("!i", 5) +
        pack("!h", bprotocol.SET_TYPE) +
        pack("!i", 6) +
        pack("!h", bprotocol.ARRAY_TYPE) +
        pack("!i", 7) +
        pack("!h", bprotocol.END_TYPE))
    java_client = Mock
    java_client.address = "127.0.0.1"
    java_client.port = 14000
    java_client.gateway_property = Mock()
    java_client.converters = Mock()
    java_client.gateway_property.auto_field = False
    java_client.gateway_property.enable_memory_management = False

    args = registry.decode_arguments(b, java_client=java_client)

    assert len(args) == 5
