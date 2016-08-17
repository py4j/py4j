# -*- coding: UTF-8 -*-
from io import BytesIO
from math import isnan
from struct import pack

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

from py4j import binary_protocol as bprotocol


def test_none_decoder():
    decoder = bprotocol.NoneDecoder()
    b = BytesIO(bytes())
    assert decoder.decode(b, bprotocol.NULL_TYPE) is None


def test_int_decoder():
    decoder = bprotocol.IntDecoder()
    b = BytesIO(pack("!i", 23))
    assert decoder.decode(b, bprotocol.INTEGER_TYPE) == 23

    b = BytesIO(pack("!q", 23))
    assert decoder.decode(b, bprotocol.LONG_TYPE) == 23


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
        b, bprotocol.PYTHON_REFERENCE_LONG_TYPE, python_proxy_pool=pool)

    assert python_instance == pool[45]


def test_java_object_long_decoder():
    with patch("py4j.java_gateway.JavaObject") as java_object_mock:
        decoder = bprotocol.JavaObjectLongDecoder()
        java_client = Mock()
        b = BytesIO(pack("!q", 45))
        java_object = decoder.decode(
            b, bprotocol.JAVA_REFERENCE_LONG_TYPE, java_client=java_client)

        assert java_object is not None
        java_object_mock.assert_called_once_with(
            45, java_client)
