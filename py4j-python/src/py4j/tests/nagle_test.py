"""Unit + integration tests for the disable_nagle helper and its
wiring across the gateway connection paths.

The helper itself is pure-Python (no JVM required). The integration
tests open real JavaGateway / ClientServer connections and inspect
the TCP_NODELAY socket option on the live socket — a regression guard
that future refactors don't drop the setting.

See java_gateway.py:disable_nagle for rationale (issue #516).
"""
import socket
import threading
import unittest
from unittest import TestCase

from py4j.java_gateway import disable_nagle


def _make_loopback_pair():
    """Return (client_sock, server_sock) both connected on loopback."""
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    port = listener.getsockname()[1]

    accepted = []

    def _accept():
        s, _ = listener.accept()
        accepted.append(s)

    t = threading.Thread(target=_accept)
    t.start()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", port))
    t.join(timeout=2)
    listener.close()

    return client, accepted[0]


class DisableNagleHelperTest(TestCase):
    """Unit tests for the helper itself."""

    def test_sets_tcp_nodelay(self):
        client, server = _make_loopback_pair()
        try:
            # Pre-condition: TCP_NODELAY is off by default.
            before = client.getsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY)
            self.assertFalse(
                before,
                "TCP_NODELAY should be off by default (got {!r})".format(
                    before))

            disable_nagle(client)

            # getsockopt's int interpretation of TCP_NODELAY varies by
            # platform (Linux returns 1, macOS may return another truthy
            # int such as 4). Test boolean semantics: "enabled".
            after = client.getsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY)
            self.assertTrue(
                after,
                "TCP_NODELAY should be enabled after disable_nagle "
                "(got {!r})".format(after))
        finally:
            client.close()
            server.close()

    def test_swallows_setsockopt_error(self):
        # Helper must not raise if the kernel rejects the option (e.g.
        # closed socket, AF_UNIX socket). Best-effort by contract.
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.close()
        disable_nagle(sock)  # must not raise


class GatewayConnectionNagleIntegrationTest(unittest.TestCase):
    """Integration: a real JavaGateway connection has TCP_NODELAY set
    on the underlying socket. Regression guard that the wiring in
    GatewayConnection.start() isn't dropped or moved before the connect."""

    def setUp(self):
        from py4j.tests.java_gateway_test import start_example_app_process
        self.p = start_example_app_process()
        from py4j.java_gateway import JavaGateway
        self.gateway = JavaGateway()

    def tearDown(self):
        from py4j.tests.java_gateway_test import safe_shutdown, safe_join
        safe_shutdown(self)
        safe_join(self.p)

    def test_gateway_connection_has_tcp_nodelay(self):
        # Force a connection to be opened by making one JVM call.
        self.gateway.jvm.java.lang.System.currentTimeMillis()

        # Grab a connection from the pool and inspect its socket.
        client = self.gateway._gateway_client
        # _give_back_connection won't help us hold a ref; pop one off
        # the deque directly (we know there's at least one after the
        # call above).
        conn = client.deque[0]
        nodelay = conn.socket.getsockopt(
            socket.IPPROTO_TCP, socket.TCP_NODELAY)
        self.assertTrue(
            nodelay,
            "GatewayConnection.start() must call disable_nagle() "
            "after socket.connect() (got {!r})".format(nodelay))

    def test_bytebuffer_array_8k_does_not_take_seconds(self):
        # Behavioral regression guard: issue #516's reproducer. With
        # Nagle enabled, ByteBuffer.allocate(8192).array() in a loop
        # of 100 took ~4.4 s due to the write-write-read interaction
        # with delayed ACK. With TCP_NODELAY enabled it should be
        # sub-second by a wide margin. 1.5 s is a generous bound that
        # holds even on slow CI runners; a Nagle regression would
        # blow well past it.
        import time
        buf = self.gateway.jvm.java.nio.ByteBuffer.allocate(8192)
        start = time.monotonic()
        for _ in range(100):
            buf.array()
        elapsed = time.monotonic() - start
        self.assertLess(
            elapsed, 1.5,
            "100x ByteBuffer.allocate(8192).array() took {:.2f}s — Nagle "
            "regression? (issue #516 baseline: ~4.4s with Nagle on, "
            "<0.05s with TCP_NODELAY on)".format(elapsed))
