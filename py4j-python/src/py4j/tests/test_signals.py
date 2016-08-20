# -*- coding: UTF-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from py4j.signals import Signal


@pytest.fixture
def signals():
    data = Mock()

    data.alert = Signal()
    data.receiver1 = Mock()
    data.instance1 = object()
    data.instance2 = object()

    class Receiver2(object):
        def __init__(self):
            self.mock = Mock()

        def receiver2_method(self, *args, **kwargs):
            self.mock(*args, **kwargs)
    data.receiver2 = Receiver2()

    data.error_receiver3 = Mock(side_effect=Exception)

    return data


def test_connect(signals):
    signals.alert.connect(signals.receiver1)
    signals.alert.connect(signals.receiver1)
    signals.alert.connect(signals.receiver2.receiver2_method)
    signals.alert.connect(signals.receiver2.receiver2_method)
    signals.alert.connect(signals.receiver1, unique_id="foo")
    signals.alert.connect(
        signals.receiver1, sender=signals.instance2,
        unique_id="bar")
    assert 4 == len(signals.alert.receivers)


def test_disconnect(signals):
    test_connect(signals)

    assert signals.alert.disconnect(signals.receiver1)

    # Already disconnected
    assert not signals.alert.disconnect(signals.receiver1)

    assert signals.alert.disconnect(signals.receiver1, unique_id="foo")

    # Sender is part of the id
    assert not signals.alert.disconnect(
        signals.receiver1, unique_id="bar")

    assert signals.alert.disconnect(
        signals.receiver1, sender=signals.instance2, unique_id="bar")

    assert signals.alert.disconnect(signals.receiver2.receiver2_method)

    assert 0 == len(signals.alert.receivers)


def test_send(signals):
    test_connect(signals)
    signals.alert.send(test_send, param1="foo", param2=3)
    assert 2 == signals.receiver1.call_count
    assert 1 == signals.receiver2.mock.call_count
    calls = signals.receiver1.call_args_list
    calls.extend(signals.receiver2.mock.call_args_list)
    for (args, kwargs) in calls:
        assert kwargs["param1"] == "foo"
        assert kwargs["param2"] == 3
        assert kwargs["sender"] == test_send


def test_send_to_sender(signals):
    test_connect(signals)
    signals.alert.send(signals.instance2, param1="foo", param2=3)
    assert 3 == signals.receiver1.call_count
    assert 1 == signals.receiver2.mock.call_count
    calls = signals.receiver1.call_args_list
    calls.extend(signals.receiver2.mock.call_args_list)
    for (args, kwargs) in calls:
        assert kwargs["param1"] == "foo"
        assert kwargs["param2"] == 3
        assert kwargs["sender"] == signals.instance2


def test_send_exception(signals):
    signals.alert.connect(signals.receiver1)
    signals.alert.connect(signals.error_receiver3)
    signals.alert.connect(signals.receiver1, "foo")

    with pytest.raises(Exception):
        signals.alert.send(test_send_exception, param1="foo", param2=3)

    assert 1 == signals.receiver1.call_count
    assert 0 == signals.receiver2.mock.call_count
