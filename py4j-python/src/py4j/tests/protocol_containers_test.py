"""Tests for get_command_part on container types + get_return_value
error semantics on malformed wire-format inputs.

ContainerEncodingTest pins that plain Python list/dict/set hit the
JavaObject reference path (which requires _get_object_id) and
correctly raise AttributeError — they need explicit conversion via
java_collections.ListConverter et al. before encoding. This is a
regression guard: if a future change adds a direct list/dict/set
branch to get_command_part, these tests force a deliberate decision.

MalformedWireFormatTest pins that get_return_value raises Py4JError
(not bare KeyError or IndexError) on unknown protocol type chars and
truncated/error-marker answers.
"""
from unittest import TestCase

from py4j import protocol as proto
from py4j.protocol import (
    get_command_part,
)


class ContainerEncodingTest(TestCase):
    """Encoding side: plain Python containers (list/dict/set) fall through
    to the JavaObject reference path and raise AttributeError —
    they require JVM-side conversion first via java_collections converters.
    """

    def setUp(self):
        class _NoPool:
            def put(self, *a, **kw):
                raise AssertionError("pool should not be used here")
        self.pool = _NoPool()

    # --- plain Python containers fall through to the JavaObject path ---

    def test_list_requires_java_object(self):
        # Plain Python lists are not encoded directly — they must first be
        # converted to a JavaList via java_collections.ListConverter.
        # The fallback calls _get_object_id() which doesn't exist on list.
        with self.assertRaises(AttributeError):
            get_command_part([1, 2, 3], self.pool)

    def test_dict_requires_java_object(self):
        with self.assertRaises(AttributeError):
            get_command_part({"a": 1, "b": 2}, self.pool)

    def test_set_requires_java_object(self):
        with self.assertRaises(AttributeError):
            get_command_part({1, 2, 3}, self.pool)

    def test_empty_list_requires_java_object(self):
        with self.assertRaises(AttributeError):
            get_command_part([], self.pool)


class MalformedWireFormatTest(TestCase):
    """get_return_value must raise Py4JError (NOT bare KeyError/IndexError)
    when given malformed wire data."""

    def test_unknown_type_char_raises_py4j_error(self):
        # 'Q' is not a defined OUTPUT_CONVERTER key (as of writing).
        bad_answer = proto.SUCCESS + "Q" + "garbage"
        with self.assertRaises(proto.Py4JError):
            proto.get_return_value(bad_answer, gateway_client=None)

    def test_empty_answer_raises_py4j_error(self):
        with self.assertRaises(proto.Py4JError):
            proto.get_return_value("", gateway_client=None)

    def test_error_marker_raises_py4j_error(self):
        # First char is ERROR — wire framing says the call failed.
        bad_answer = proto.ERROR + "n"  # null payload
        with self.assertRaises(proto.Py4JError):
            proto.get_return_value(bad_answer, gateway_client=None)
