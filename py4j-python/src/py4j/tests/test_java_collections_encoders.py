try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

from py4j import java_collections
from py4j import binary_protocol as bprotocol


def test_python_list_encoder():
    ArrayListInstanceMock = Mock()
    ArrayListInstanceMock._get_object_id.return_value = 1
    ArrayListMock = Mock(return_value=ArrayListInstanceMock)
    JavaClassMock = Mock(return_value=ArrayListMock)

    with patch("py4j.java_collections.JavaClass", new=JavaClassMock):
        encoder = java_collections.PythonListEncoder()
        encoded = encoder.encode([1, 2, 3], list, java_client=Mock())
        assert encoded.type == bprotocol.JAVA_REFERENCE_TYPE
        assert encoded.size is None
        assert len(encoded.value) == 8

        encoded = encoder.encode_specific([1, 2, 3], list, java_client=Mock())
        assert encoded.type == bprotocol.JAVA_REFERENCE_TYPE
        assert encoded.size is None
        assert len(encoded.value) == 8

        assert encoder.encode(45, int) == bprotocol.CANNOT_ENCODE
