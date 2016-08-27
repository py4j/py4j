try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

import pytest

from py4j import protocol, binary_protocol as bprotocol, java_gateway


def test_java_import():
    decoder_registry = bprotocol.DecoderRegistry.get_default_decoder_registry()
    jvm_view = Mock()
    jvm_view._id = 123
    jvm_view._gateway_client = Mock()
    jvm_view._gateway_client.decoder_registry = decoder_registry
    jvm_view._gateway_client.send_command = Mock(
        return_value=bprotocol.DecodedArgument(
            bprotocol.SUCCESS_TYPE, None))
    assert java_gateway.java_import(
        jvm_view, "java.util.ArrayList") is None
    jvm_view._gateway_client.encoder_registry.encode_command_lazy.\
        assert_called_with(
            bprotocol.JVM_IMPORT_SUB_COMMAND, 123, "java.util.ArrayList",
            java_client=jvm_view._gateway_client)


def test_get_field_success():
    decoder_registry = bprotocol.DecoderRegistry.get_default_decoder_registry()
    java_object = Mock()
    java_client = Mock()
    java_client.decoder_registry = decoder_registry
    java_client.send_command = Mock(
        return_value=bprotocol.DecodedArgument(
            bprotocol.INTEGER_TYPE, 123))
    java_object._gateway_client = java_client
    java_object._target_id = 234

    assert java_gateway.get_field(java_object, "bob") == 123
    java_client.encoder_registry.encode_command_lazy.\
        assert_called_with(
            bprotocol.FIELD_GET_SUBCOMMAND, java_object, "bob",
            java_client=java_client)


def test_get_field_error():
    decoder_registry = bprotocol.DecoderRegistry.get_default_decoder_registry()
    java_object = Mock()
    java_client = Mock()
    java_client.decoder_registry = decoder_registry
    java_client.send_command = Mock(
        return_value=bprotocol.DecodedArgument(
            bprotocol.NO_MEMBER_TYPE, None))
    java_object._gateway_client = java_client
    java_object._target_id = 234

    with pytest.raises(protocol.Py4JError):
        java_gateway.get_field(java_object, "bob")


def test_set_field_success():
    decoder_registry = bprotocol.DecoderRegistry.get_default_decoder_registry()
    java_object = Mock()
    java_client = Mock()
    java_client.decoder_registry = decoder_registry
    java_client.send_command = Mock(
        return_value=bprotocol.DecodedArgument(
            bprotocol.SUCCESS_TYPE, None))
    java_object._gateway_client = java_client
    java_object._target_id = 234

    assert java_gateway.set_field(java_object, "bob", 123) is None
    java_client.encoder_registry.encode_command_lazy.\
        assert_called_with(
            bprotocol.FIELD_SET_SUBCOMMAND, java_object, "bob",
            123, java_client=java_client)


def test_set_field_error():
    decoder_registry = bprotocol.DecoderRegistry.get_default_decoder_registry()
    java_object = Mock()
    java_client = Mock()
    java_client.decoder_registry = decoder_registry
    java_client.send_command = Mock(
        return_value=bprotocol.DecodedArgument(
            bprotocol.NO_MEMBER_TYPE, None))
    java_object._gateway_client = java_client
    java_object._target_id = 234

    with pytest.raises(protocol.Py4JError):
        java_gateway.set_field(java_object, "bob", 123)


def test_quiet_close():
    error_mock = Mock()
    error_mock.close = Mock(side_effet=ValueError)
    assert java_gateway.quiet_close(None) is None
    assert java_gateway.quiet_close(Mock()) is None
    assert java_gateway.quiet_close(error_mock) is None


def test_quiet_shutdown():
    error_mock = Mock()
    error_mock.shutdown = Mock(side_effet=ValueError)
    assert java_gateway.quiet_shutdown(None) is None
    assert java_gateway.quiet_shutdown(Mock()) is None
    assert java_gateway.quiet_shutdown(error_mock) is None
