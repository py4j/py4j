try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

import pytest

from py4j import (
    finalizer, protocol, binary_protocol as bprotocol, java_gateway)


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


def test_gateway_help_java_object():
    # Because we call getattr_static, we cannot mock :-()
    class JavaObjectMock(object):
        def _get_object_id(self):
            pass
    decoder_registry = bprotocol.DecoderRegistry.get_default_decoder_registry()
    java_client = Mock()
    java_client.send_command = Mock(
        return_value=bprotocol.DecodedArgument(
            bprotocol.STRING_TYPE, "Help Page 1"))
    java_client.decoder_registry = decoder_registry

    assert java_gateway.gateway_help(
        java_client, JavaObjectMock(), "member", True, False) == "Help Page 1"


def test_gateway_help_java_class():
    # Because we call getattr_static, we cannot mock :-()
    class JavaClassMock(object):
        def __init__(self):
            self._fqn = "com.foo.Bar"
    decoder_registry = bprotocol.DecoderRegistry.get_default_decoder_registry()
    java_client = Mock()
    java_client.send_command = Mock(
        return_value=bprotocol.DecodedArgument(
            bprotocol.STRING_TYPE, "Help Page 1"))
    java_client.decoder_registry = decoder_registry

    assert java_gateway.gateway_help(
        java_client, JavaClassMock(), "member", True, False) == "Help Page 1"


def test_gateway_help_java_member():
    # Because we call getattr_static, we cannot mock :-()
    class JavaObjectMock(object):
        def _get_object_id(self):
            pass

    class JavaMemberMock(object):
        def __init__(self):
            self.container = JavaObjectMock()
            self.name = "foo"
    decoder_registry = bprotocol.DecoderRegistry.get_default_decoder_registry()
    java_client = Mock()
    java_client.send_command = Mock(
        return_value=bprotocol.DecodedArgument(
            bprotocol.STRING_TYPE, "Help Page 1"))
    java_client.decoder_registry = decoder_registry

    assert java_gateway.gateway_help(
        java_client, JavaMemberMock(), None, True, False) == "Help Page 1"


def test_gateway_help_errors():

    class JavaObjectMock(object):
        def _get_object_id(self):
            pass

    class JavaMemberMock(object):
        def __init__(self):
            self.container = JavaObjectMock()
            self.name = "foo"

    decoder_registry = bprotocol.DecoderRegistry.get_default_decoder_registry()
    java_client = Mock()
    java_client.send_command = Mock(
        return_value=bprotocol.DecodedArgument(
            bprotocol.STRING_TYPE, "Help Page 1"))
    java_client.decoder_registry = decoder_registry

    # Do not pass pattern with JavaMember
    with pytest.raises(protocol.Py4JError):
        java_gateway.gateway_help(
            java_client, JavaMemberMock(), "pattern should be none", True,
            False)

    # Not a Java Object, Class, or Member
    with pytest.raises(protocol.Py4JError):
        java_gateway.gateway_help(
            java_client, "Hello", "pattern", True, False)


def test_garbage_collect_object():
    address = "127.0.0.1"
    port = 25333
    target_id = 1234

    finalizer.ThreadSafeFinalizer.add_finalizer("127.0.0.1253331234", object())

    encoder_registry = bprotocol.EncoderRegistry.get_default_encoder_registry()
    decoder_registry = bprotocol.DecoderRegistry.get_default_decoder_registry()
    java_client = Mock()
    java_client.address = address
    java_client.port = port
    java_client.is_connected = True
    java_client.send_command = Mock(
        return_value=bprotocol.DecodedArgument(
            bprotocol.VOID_TYPE, None))
    java_client.decoder_registry = decoder_registry
    java_client.encoder_registry = encoder_registry

    return_value = java_gateway._garbage_collect_object(java_client, target_id)

    assert return_value is None
    assert java_client.send_command.called

    # Object is not registered: will still go through the method
    return_value = java_gateway._garbage_collect_object(java_client, 12345)

    assert return_value is None
    assert java_client.send_command.call_count == 2


def test_garbage_collect_object_errors():
    address = "127.0.0.1"
    port = 25333
    target_id = 1234

    encoder_registry = bprotocol.EncoderRegistry.get_default_encoder_registry()
    decoder_registry = bprotocol.DecoderRegistry.get_default_decoder_registry()
    java_client = Mock()
    java_client.address = address
    java_client.port = port
    java_client.is_connected = True
    java_client.send_command = Mock(
        return_value=bprotocol.DecodedArgument(
            bprotocol.VOID_TYPE, None))
    java_client.decoder_registry = decoder_registry
    java_client.encoder_registry = encoder_registry

    # Nothing to do
    finalizer.ThreadSafeFinalizer.add_finalizer("127.0.0.1253331234", object())
    java_client.is_connected = False
    java_gateway._garbage_collect_object(java_client, target_id)
    assert not java_client.send_command.called

    # Exception is swallowed
    java_client.is_connected = True
    java_client.send_command = Mock(
        return_value=bprotocol.DecodedArgument(
            bprotocol.EXCEPTION_TYPE, 123))
    assert java_gateway._garbage_collect_object(java_client, target_id) is None
    assert java_client.send_command.called
