/******************************************************************************
 * Copyright (c) 2009-2022, Barthelemy Dagenais and individual contributors.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * - Redistributions of source code must retain the above copyright notice,
 * this list of conditions and the following disclaimer.
 *
 * - Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 *
 * - The name of the author may not be used to endorse or promote products
 * derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 *****************************************************************************/
package py4j;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import java.net.InetAddress;
import java.net.Socket;

import javax.net.ServerSocketFactory;
import javax.net.SocketFactory;

import org.junit.Test;

public class ClientServerTest {

	@Test
	public void testListenerClientServer() {
		TestListener listener = new TestListener();
		// Use preStartListener so the listener is attached before the
		// server thread spawns (which fires serverStarted asynchronously).
		// Without this, the listener would race the constructor's
		// auto-start path and miss serverStarted on fast machines. The
		// preStartListener builder method was added to address exactly
		// this race; see ClientServerBuilder.preStartListener javadoc.
		ClientServer server1 = new ClientServer.ClientServerBuilder(null).preStartListener(listener).build();
		// Listener events fire from a background thread (GatewayServer.run()),
		// so startServer/shutdown return before serverStarted/serverStopped
		// land in listener.values. Poll for the expected events instead of
		// blind-sleeping: a healthy runner finishes in tens of ms, but a
		// loaded CI runner can take seconds.
		waitForListenerSize(listener, 1, 10000);
		server1.shutdown();
		waitForListenerSize(listener, 4, 10000);
		// Started, PreShutdown, Stopped, PostShutdown
		// But order cannot be guaranteed because two threads are competing.
		assertTrue(listener.values.contains(new Long(1)));
		assertTrue(listener.values.contains(new Long(10)));
		assertTrue(listener.values.contains(new Long(1000)));
		assertTrue(listener.values.contains(new Long(10000)));
		// With the run() catch-handler fix in PR-D (skip fireServerError
		// when isShutdown is set), the 4 expected events are the only ones
		// that fire on a clean shutdown.
		assertEquals(4, listener.values.size());
	}

	private static void waitForListenerSize(TestListener listener, int target, long timeoutMs) {
		long deadline = System.currentTimeMillis() + timeoutMs;
		while (listener.values.size() < target && System.currentTimeMillis() < deadline) {
			try {
				Thread.sleep(20);
			} catch (InterruptedException e) {
				Thread.currentThread().interrupt();
				return;
			}
		}
	}

	@Test
	public void testClientServerBuilder() {
		ClientServer server = new ClientServer.ClientServerBuilder(null).javaPort(0).build();
		Py4JJavaServer javaServer = server.getJavaServer();
		server.startServer(true);
		try {
			Thread.sleep(250);
		} catch (Exception e) {

		}
		int listeningPort = javaServer.getListeningPort();
		assertTrue(listeningPort > 0);
		assertTrue(javaServer.getPort() != listeningPort);
		server.shutdown();
	}

	@Test
	public void testClientServerBuilderUsesConfiguredJavaAddress() throws Exception {
		InetAddress address = InetAddress.getByName("127.0.0.2");
		ClientServer server = new ClientServer.ClientServerBuilder(null).javaPort(0).javaAddress(address)
				.autoStartJavaServer(false).build();
		try {
			assertEquals(address, server.getJavaServer().getAddress());
		} finally {
			server.shutdown();
		}
	}

	@Test
	public void testClientServerBuilderDefaultsJavaAddress() {
		ClientServer server = new ClientServer.ClientServerBuilder(null).javaPort(0).autoStartJavaServer(false)
				.build();
		try {
			assertEquals(GatewayServer.defaultAddress(), server.getJavaServer().getAddress());
		} finally {
			server.shutdown();
		}
	}

	@Test
	public void testLegacyClientServerConstructorDefaultsJavaAddress() {
		ClientServer server = new ClientServer(0, GatewayServer.defaultAddress(), 0,
				GatewayServer.defaultAddress(), GatewayServer.DEFAULT_CONNECT_TIMEOUT,
				GatewayServer.DEFAULT_READ_TIMEOUT, ServerSocketFactory.getDefault(), SocketFactory.getDefault(), null,
				false, true);
		try {
			assertEquals(GatewayServer.defaultAddress(), server.getJavaServer().getAddress());
		} finally {
			server.shutdown();
		}
	}

	/**
	 * Regression test: when listeners are registered through
	 * {@code preStartListener}, they must observe the {@code serverStarted}
	 * event (no race with auto-start in the constructor).
	 *
	 * Before the fix, the only way to observe the {@code serverStarted}
	 * event with the default builder (autoStartJavaServer=true) was to
	 * race-attach the listener after construction; the listener typically
	 * missed the event on fast machines. The new {@code preStartListener}
	 * builder method registers the listener before the server thread is
	 * spawned.
	 */
	@Test
	public void testPreStartListenerObservesServerStarted() {
		TestListener listener = new TestListener();
		ClientServer server = new ClientServer.ClientServerBuilder(null).javaPort(0).preStartListener(listener).build();
		// Even on the fastest machines, the listener must catch serverStarted.
		long deadline = System.currentTimeMillis() + 5000;
		while (!listener.values.contains(new Long(1)) && System.currentTimeMillis() < deadline) {
			try {
				Thread.sleep(20);
			} catch (InterruptedException e) {
				Thread.currentThread().interrupt();
				break;
			}
		}
		assertTrue("preStartListener missed serverStarted", listener.values.contains(new Long(1)));
		server.shutdown();
	}

	/**
	 * Regression test: a normal {@code shutdown()} on a {@link ClientServer}
	 * must NOT fire {@code serverError}.
	 *
	 * Same root cause as
	 * {@code GatewayServerTest.testListenerNoSpuriousErrorOnShutdown}: the
	 * server thread's catch handler used to route the SocketException from
	 * normal shutdown through {@code fireServerError}.
	 */
	@Test
	public void testListenerNoSpuriousErrorOnShutdown() {
		TestListener listener = new TestListener();
		ClientServer server = new ClientServer.ClientServerBuilder(null).javaPort(0).preStartListener(listener).build();
		try {
			Thread.sleep(250);
		} catch (Exception e) {
		}
		server.shutdown();
		try {
			Thread.sleep(250);
		} catch (Exception e) {
		}
		// 100 = serverError. It must NOT fire on a clean shutdown.
		assertFalse("serverError fired during a normal shutdown", listener.values.contains(new Long(100)));
	}

	/**
	 * Regression test: when {@code preStartListener} is combined with
	 * {@code autoStartJavaServer(false)}, the listener must be attached
	 * but the server must NOT auto-start in the constructor — the user
	 * is responsible for calling {@code startServer()} explicitly.
	 */
	@Test
	public void testPreStartListenerWithAutoStartFalse() throws InterruptedException {
		TestListener listener = new TestListener();
		ClientServer server = new ClientServer.ClientServerBuilder(null).javaPort(0).autoStartJavaServer(false)
				.preStartListener(listener).build();
		// With autoStartJavaServer(false), no events should fire yet.
		Thread.sleep(200);
		assertEquals("server should not be running yet", 0, listener.values.size());
		// Now start the server and verify the listener catches serverStarted.
		server.startServer(true);
		long deadline = System.currentTimeMillis() + 5000;
		while (!listener.values.contains(new Long(1)) && System.currentTimeMillis() < deadline) {
			Thread.sleep(20);
		}
		assertTrue("listener missed serverStarted after explicit startServer", listener.values.contains(new Long(1)));
		server.shutdown();
	}

	/**
	 * Regression test: multiple {@code preStartListener} calls register
	 * each listener, and all of them observe the lifecycle events.
	 */
	@Test
	public void testMultiplePreStartListeners() throws InterruptedException {
		TestListener listener1 = new TestListener();
		TestListener listener2 = new TestListener();
		ClientServer server = new ClientServer.ClientServerBuilder(null).javaPort(0).preStartListener(listener1)
				.preStartListener(listener2).build();
		long deadline = System.currentTimeMillis() + 5000;
		while ((!listener1.values.contains(new Long(1)) || !listener2.values.contains(new Long(1)))
				&& System.currentTimeMillis() < deadline) {
			Thread.sleep(20);
		}
		assertTrue("first listener missed serverStarted", listener1.values.contains(new Long(1)));
		assertTrue("second listener missed serverStarted", listener2.values.contains(new Long(1)));
		server.shutdown();
	}

	/**
	 * Regression test: {@code ClientServer.shutdown(int gracePeriodMs)}
	 * delegates to the underlying {@code Py4JJavaServer.shutdown(true,
	 * gracePeriodMs)}. The grace period must be honored; with an active
	 * connection that doesn't drain, the shutdown should return at the
	 * deadline (not earlier).
	 */
	@Test
	public void testClientServerGracefulShutdown() throws Exception {
		ClientServer cs = new ClientServer.ClientServerBuilder(null).javaPort(0).build();
		Thread.sleep(100);
		Py4JJavaServer javaServer = cs.getJavaServer();
		final int port = javaServer.getListeningPort();
		// Open a connection so the grace-period drain has work to do.
		Socket client = new Socket("127.0.0.1", port);
		Thread.sleep(100);

		long start = System.currentTimeMillis();
		// 500ms grace period; client never closes — shutdown should respect
		// the deadline.
		cs.shutdown(500);
		long elapsed = System.currentTimeMillis() - start;
		assertTrue("ClientServer.shutdown(int) returned before deadline: " + elapsed + "ms", elapsed >= 400);
		assertTrue("ClientServer.shutdown(int) took much longer than deadline: " + elapsed + "ms", elapsed < 2000);

		try {
			client.close();
		} catch (Exception ignored) {
		}
	}
}
