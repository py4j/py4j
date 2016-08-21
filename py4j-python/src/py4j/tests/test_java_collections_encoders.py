try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

from py4j import java_collections
from py4j import binary_protocol as bprotocol


def assert_python_collection_long(encoded):
    assert encoded.type == bprotocol.JAVA_REFERENCE_TYPE
    assert encoded.size is None
    assert len(encoded.value) == 8


def test_python_list_encoder():
    ArrayListInstanceMock = Mock()
    ArrayListInstanceMock._get_object_id.return_value = 1
    ArrayListMock = Mock(return_value=ArrayListInstanceMock)
    JavaClassMock = Mock(return_value=ArrayListMock)
    registry = bprotocol.EncoderRegistry.get_default_encoder_registry()

    with patch("py4j.java_collections.JavaClass", new=JavaClassMock):
        encoder = java_collections.PythonListEncoder()
        encoder.set_encoder_registry(registry)
        encoded = encoder.encode([1, 2, 3], list, java_client=Mock())
        assert_python_collection_long(encoded)

        encoded = encoder.encode_specific([1, 2, 3], list, java_client=Mock())
        assert_python_collection_long(encoded)

        assert encoder.encode(45, int) == bprotocol.CANNOT_ENCODE


def test_python_set_encoder():
    HashSetInstanceMock = Mock()
    HashSetInstanceMock._get_object_id.return_value = 1
    HashSetMock = Mock(return_value=HashSetInstanceMock)
    JavaClassMock = Mock(return_value=HashSetMock)
    registry = bprotocol.EncoderRegistry.get_default_encoder_registry()

    with patch("py4j.java_collections.JavaClass", new=JavaClassMock):
        encoder = java_collections.PythonListEncoder()
        encoder.set_encoder_registry(registry)
        encoded = encoder.encode(set([1, 2, 3]), list, java_client=Mock())
        assert_python_collection_long(encoded)

        encoded = encoder.encode_specific(
            set([1, 2, 3]), list, java_client=Mock())
        assert_python_collection_long(encoded)

        assert encoder.encode("hello", int) == bprotocol.CANNOT_ENCODE


def test_python_map_encoder():
    HashMapInstanceMock = Mock()
    HashMapInstanceMock._get_object_id.return_value = 1
    HashMapMock = Mock(return_value=HashMapInstanceMock)
    JavaClassMock = Mock(return_value=HashMapMock)
    registry = bprotocol.EncoderRegistry.get_default_encoder_registry()

    with patch("py4j.java_collections.JavaClass", new=JavaClassMock):
        encoder = java_collections.PythonListEncoder()
        encoder.set_encoder_registry(registry)
        encoded = encoder.encode({"a": 1}, list, java_client=Mock())
        assert_python_collection_long(encoded)

        encoded = encoder.encode_specific({"a": 1}, list, java_client=Mock())
        assert_python_collection_long(encoded)

        assert encoder.encode("hello", int) == bprotocol.CANNOT_ENCODE
