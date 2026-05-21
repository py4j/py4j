"""
Pure-protocol unit tests covering Python 2 / 3 boundary semantics.

Pinned here so the Python 2 removal can't silently regress the
externally-visible behaviour of ``py4j.compat`` (which downstream
projects still import from) or the protocol-encoding paths that
deal with ``bytes`` vs ``str`` distinctions.

No JVM dependency — fast pure-Python tests.
"""
import unittest
from decimal import Decimal

from py4j.protocol import (
    decode_bytearray, encode_bytearray, encode_float,
    escape_new_line, unescape_new_line, get_command_part,
    smart_decode,
    NULL_TYPE, BOOLEAN_TYPE, INTEGER_TYPE, LONG_TYPE, DOUBLE_TYPE,
    BYTES_TYPE, STRING_TYPE, JAVA_INFINITY, JAVA_NEGATIVE_INFINITY,
    JAVA_NAN, JAVA_MAX_INT, JAVA_MIN_INT,
)


class EncodeBytearrayRoundTripTest(unittest.TestCase):
    """``encode_bytearray`` / ``decode_bytearray`` round-trip protected
    after the Python 2 removal collapsed the ``bytearray2`` /
    ``bytestr`` aliases into ``bytes``.
    """

    def test_round_trip_bytes(self):
        original = b"\x00\x01\x02\xff\xfe\xfd"
        encoded = encode_bytearray(original)
        self.assertIsInstance(encoded, str)
        self.assertEqual(decode_bytearray(encoded), original)

    def test_round_trip_bytearray(self):
        original = bytearray(b"abc\x00xyz")
        encoded = encode_bytearray(original)
        self.assertIsInstance(encoded, str)
        # decode returns bytes, but content must compare equal.
        self.assertEqual(decode_bytearray(encoded), bytes(original))

    def test_round_trip_empty(self):
        self.assertEqual(decode_bytearray(encode_bytearray(b"")), b"")

    def test_round_trip_high_bytes(self):
        # All single-byte values, exercises the full 0-255 range.
        original = bytes(range(256))
        self.assertEqual(decode_bytearray(encode_bytearray(original)), original)


class EscapeNewLineTest(unittest.TestCase):
    """``escape_new_line`` / ``unescape_new_line`` round-trip protected.
    The function preserves a long-standing wrapping behaviour for
    ``bytes`` inputs (via ``smart_decode``) so removing ``smart_decode``
    here would be a behaviour change, not a Python 2 removal.
    """

    def test_str_passthrough_simple(self):
        self.assertEqual(escape_new_line("hello"), "hello")

    def test_escapes_backslash_then_newlines(self):
        # Order matters: backslash must be doubled first so that the
        # ``\n`` / ``\r`` insertions don't get re-escaped.
        self.assertEqual(escape_new_line("a\\b\rc\nd"), "a\\\\b\\rc\\nd")

    def test_round_trip_with_unescape(self):
        original = "first line\nsecond\tline\rthird\\fourth"
        self.assertEqual(unescape_new_line(escape_new_line(original)), original)

    def test_falsy_passthrough(self):
        # Documented behaviour: empty / None returns input unchanged.
        self.assertEqual(escape_new_line(""), "")
        self.assertIsNone(escape_new_line(None))


class GetCommandPartTest(unittest.TestCase):
    """Spot-check ``get_command_part`` after the type-check aliases
    (``isinstance(x, long)`` etc.) were collapsed into native py3
    types.
    """

    def _strip(self, s):
        self.assertTrue(s.endswith("\n"))
        return s[:-1]

    def test_none_uses_null_prefix(self):
        self.assertEqual(self._strip(get_command_part(None)), NULL_TYPE.strip())

    def test_bool_dispatched_before_int(self):
        # ``isinstance(True, int)`` is True in Python — the bool branch
        # must run first so booleans don't get INTEGER-encoded.
        self.assertTrue(
            self._strip(get_command_part(True)).startswith(BOOLEAN_TYPE))
        self.assertTrue(
            self._strip(get_command_part(False)).startswith(BOOLEAN_TYPE))

    def test_small_int_uses_integer_prefix(self):
        self.assertEqual(
            self._strip(get_command_part(42)),
            INTEGER_TYPE + "42")

    def test_int_at_java_max_uses_integer_prefix(self):
        # Inclusive boundary.
        self.assertEqual(
            self._strip(get_command_part(JAVA_MAX_INT)),
            INTEGER_TYPE + str(JAVA_MAX_INT))

    def test_int_above_java_max_uses_long_prefix(self):
        big = JAVA_MAX_INT + 1
        self.assertEqual(
            self._strip(get_command_part(big)),
            LONG_TYPE + str(big))

    def test_int_below_java_min_uses_long_prefix(self):
        small = JAVA_MIN_INT - 1
        self.assertEqual(
            self._strip(get_command_part(small)),
            LONG_TYPE + str(small))

    def test_float_uses_double_prefix(self):
        self.assertEqual(
            self._strip(get_command_part(0.5)),
            DOUBLE_TYPE + "0.5")

    def test_str_uses_string_prefix_with_escaping(self):
        out = self._strip(get_command_part("a\nb"))
        self.assertEqual(out, STRING_TYPE + "a\\nb")

    def test_bytes_uses_bytes_prefix(self):
        out = self._strip(get_command_part(b"abc"))
        self.assertTrue(out.startswith(BYTES_TYPE))

    def test_bytearray_uses_bytes_prefix(self):
        out = self._strip(get_command_part(bytearray(b"abc")))
        self.assertTrue(out.startswith(BYTES_TYPE))


class EncodeFloatTest(unittest.TestCase):
    """``encode_float`` after the ``smart_decode(repr(...))`` /
    ``unicode(...)`` aliases were inlined. Java-side spellings for
    inf / -inf / NaN preserved.
    """

    def test_positive_infinity(self):
        self.assertEqual(encode_float(float("inf")), JAVA_INFINITY)

    def test_negative_infinity(self):
        self.assertEqual(encode_float(float("-inf")), JAVA_NEGATIVE_INFINITY)

    def test_nan(self):
        self.assertEqual(encode_float(float("nan")), JAVA_NAN)

    def test_finite_float(self):
        self.assertEqual(encode_float(1.0), "1.0")


class SmartDecodeTest(unittest.TestCase):
    """``smart_decode`` body was rewritten with native py3 types
    (``str`` instead of ``unicode``; ``bytes`` instead of ``bytestr``).
    Function-level behaviour must be unchanged.
    """

    def test_str_input_returns_input_unchanged(self):
        self.assertEqual(smart_decode("hello"), "hello")

    def test_bytes_input_decodes_as_utf8(self):
        self.assertEqual(smart_decode(b"hello"), "hello")
        self.assertEqual(smart_decode("café".encode("utf-8")), "café")

    def test_non_string_falls_back_to_str(self):
        self.assertEqual(smart_decode(123), "123")
        self.assertEqual(smart_decode(0.5), "0.5")
        self.assertEqual(smart_decode(None), "None")


class CompatModuleBackcompatTest(unittest.TestCase):
    """``py4j.compat`` is kept around as a soft-deprecated shim for any
    external callers that imported its py2/3 names
    (``from py4j.compat import unicode``, etc.). This pins every
    exported name to its py3 equivalent so a future cleanup of the
    module can't silently break downstream imports.
    """

    def test_compat_exports_resolve(self):
        from py4j.compat import (   # noqa: F401
            items, iteritems, range, long, basestring, unicode,
            bytearray2, unichr, bytestr, tobytestr, isbytestr,
            ispython3bytestr, isbytearray, bytetoint, bytetostr,
            strtobyte, Queue, Empty, hasattr2, CompatThread,
            version_info,
        )

    def test_compat_aliases_resolve_to_py3_builtins(self):
        from py4j import compat
        self.assertIs(compat.long, int)
        self.assertIs(compat.basestring, str)
        self.assertIs(compat.unicode, str)
        self.assertIs(compat.bytestr, bytes)
        self.assertIs(compat.range, range)
        self.assertIs(compat.unichr, chr)

    def test_compat_helpers_use_py3_semantics(self):
        from py4j import compat
        self.assertTrue(compat.isbytestr(b""))
        self.assertFalse(compat.isbytestr(""))
        self.assertTrue(compat.ispython3bytestr(b""))
        self.assertFalse(compat.ispython3bytestr(""))
        self.assertTrue(compat.isbytearray(bytearray()))
        self.assertFalse(compat.isbytearray(b""))
        self.assertEqual(compat.bytetoint(b"a"[0]), b"a"[0])
        self.assertEqual(compat.bytetostr(b"abc"), "abc")
        self.assertEqual(compat.strtobyte("abc"), b"abc")
        self.assertEqual(compat.items({"a": 1}), [("a", 1)])
        self.assertEqual(list(compat.iteritems({"a": 1})), [("a", 1)])

    def test_compat_thread_is_threading_thread(self):
        from threading import Thread
        from py4j.compat import CompatThread
        self.assertIs(CompatThread, Thread)

    def test_compat_queue_is_stdlib_queue(self):
        from queue import Queue as StdQueue, Empty as StdEmpty
        from py4j.compat import Queue, Empty
        self.assertIs(Queue, StdQueue)
        self.assertIs(Empty, StdEmpty)


class DecimalEncodingTest(unittest.TestCase):
    """Decimal precision and special-value handling in the wire protocol.

    py4j currently routes Decimal through smart_decode(repr(d)). These
    tests pin that contract: precision must survive round-trip, and
    Infinity/NaN must not silently corrupt the wire."""

    def setUp(self):
        class _NoPool:
            def put(self, *a, **kw):
                raise AssertionError("pool should not be used here")
        self.pool = _NoPool()

    def test_high_precision_decimal_preserved_in_wire_text(self):
        d = Decimal("123.45678901234567890123")
        out = get_command_part(d, self.pool)
        # The decimal's text form must appear verbatim in the wire
        # output — that's the only way the Java side can reconstruct
        # the exact value.
        self.assertIn("123.45678901234567890123", out)

    def test_decimal_infinity_encodes_verbatim(self):
        # Pin the contract: Decimal("Infinity") flows through
        # smart_decode(repr(d)) and the text "Infinity" appears in the
        # wire output. If a future refactor silently re-routes Decimal
        # encoding (e.g., via float()), this regresses to "inf" or
        # something else and the test catches it.
        out = get_command_part(Decimal("Infinity"), self.pool)
        self.assertIn("Infinity", out)

    def test_decimal_nan_encodes_verbatim(self):
        # Same contract as Infinity. Pinning the literal "NaN" string
        # in the wire output prevents silent corruption.
        out = get_command_part(Decimal("NaN"), self.pool)
        self.assertIn("NaN", out)

    def test_negative_decimal(self):
        out = get_command_part(Decimal("-1.5"), self.pool)
        self.assertIn("-1.5", out)


class StringEscapingEdgeCasesTest(unittest.TestCase):
    """escape_new_line / unescape_new_line round-trip on boundary inputs.

    Existing tests cover plain ASCII. These add: UTF-8 (CJK + emoji),
    consecutive backslashes, mixed CRLF, embedded nulls. Each is a
    silent-corruption risk that the current code happens to handle
    correctly — pin it before any state-machine rewrite (deferred
    from this PR; gated on this coverage)."""

    def _roundtrip(self, s):
        return unescape_new_line(escape_new_line(s))

    def test_utf8_cjk(self):
        s = "\u4e2d\u6587\u30c6\u30b9\u30c8"  # 中文テスト
        self.assertEqual(self._roundtrip(s), s)

    def test_utf8_emoji(self):
        s = "hello \U0001F600 world \U0001F4A9"
        self.assertEqual(self._roundtrip(s), s)

    def test_consecutive_backslashes(self):
        s = "a\\\\\\b"  # three actual backslashes + b
        self.assertEqual(self._roundtrip(s), s)

    def test_mixed_crlf(self):
        s = "line1\r\nline2\nline3\rline4"
        self.assertEqual(self._roundtrip(s), s)

    def test_null_byte_in_string(self):
        s = "before\x00after"
        self.assertEqual(self._roundtrip(s), s)

    def test_empty_string(self):
        self.assertEqual(self._roundtrip(""), "")

    def test_only_special_chars(self):
        # CRLF + 2 backslashes + CRLF + 1 backslash — exercises the
        # interaction between the newline-escape and backslash-escape
        # paths in a single string (neither test_mixed_crlf nor
        # test_consecutive_backslashes covers this combination).
        s = "\r\n\\\\\r\n\\"
        self.assertEqual(self._roundtrip(s), s)


class EscapeNewLineBytesInputSafetyTest(unittest.TestCase):
    """Pins the bytes-input safety contract on escape_new_line.

    escape_new_line's ``smart_decode(original)`` is a defensive measure
    that lets bytes inputs pass through cleanly — see the docstring of
    escape_new_line for the full rationale. PR #575's perf review
    proposed dropping this smart_decode; doing so makes
    ``bytes.replace("str", "str")`` raise TypeError, breaking the
    auth-token round-trip path (testGatewayAuth) and any other path
    that hands escape_new_line a bytes input without explicit decoding.

    If a future refactor drops smart_decode from escape_new_line, these
    tests fail immediately — catching the regression before CI's
    integration tests need to spin up a JVM."""

    def test_bytes_input_decoded_as_utf8(self):
        # ASCII bytes round-trip through escape_new_line as if they
        # were str — smart_decode does the conversion.
        result = escape_new_line(b"hello\nworld")
        self.assertEqual(result, "hello\\nworld")

    def test_str_input_passes_through(self):
        # str inputs are the common case; smart_decode is a single
        # isinstance hit for these.
        result = escape_new_line("hello\nworld")
        self.assertEqual(result, "hello\\nworld")

    def test_bytes_input_with_utf8_payload(self):
        # Non-ASCII bytes (UTF-8 encoded) decode correctly via
        # smart_decode("utf-8") — auth tokens or other identifiers
        # may contain UTF-8 bytes if read from stdout in binary mode.
        s = "\u4e2d\u6587"  # "中文"
        result = escape_new_line(s.encode("utf-8"))
        self.assertEqual(result, s)

    def test_empty_bytes_passes_through(self):
        # The falsy-passthrough branch handles both b"" and "".
        self.assertEqual(escape_new_line(b""), b"")


if __name__ == "__main__":
    unittest.main()
