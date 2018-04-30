/******************************************************************************
 * Copyright (c) 2009-2018, Barthelemy Dagenais and individual contributors.
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
import static org.junit.Assert.fail;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.InetAddress;
import java.net.Socket;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

import org.junit.Test;

import py4j.commands.AuthCommand;
import py4j.commands.HelpPageCommand;

public class GatewayServerTest {

	@Test
	public void testDoubleListen() {
		GatewayServer server1 = new GatewayServer.GatewayServerBuilder().entryPoint(null).build();
		GatewayServer server2 = new GatewayServer.GatewayServerBuilder().entryPoint(null).build();
		boolean valid = false;

		try {
			server1.start();
			server2.start();
			valid = false;
		} catch (Py4JNetworkException network) {
			valid = true;
		} catch (Exception e) {
			valid = false;
		}

		server1.shutdown();
		server2.shutdown();

		assertTrue(valid);
	}

	@Test
	public void testListener() {
		TestListener listener = new TestListener();
		GatewayServer server1 = new GatewayServer(null);
		server1.addListener(listener);
		server1.start();
		try {
			Thread.sleep(250);
		} catch (Exception e) {

		}
		server1.shutdown();
		try {
			Thread.sleep(250);
		} catch (Exception e) {

		}
		// Started, PreShutdown, Stopped, PostShutdown
		// But order cannot be guaranteed because two threads are competing.
		assertTrue(listener.values.contains(new Long(1)));
		assertTrue(listener.values.contains(new Long(10)));
		assertTrue(listener.values.contains(new Long(1000)));
		assertTrue(listener.values.contains(new Long(10000)));
		assertEquals(4, listener.values.size());
	}

	@Test
	public void testEphemeralPort() {
		GatewayServer server = new GatewayServer(null, 0);
		server.start(true);
		try {
			Thread.sleep(250);
		} catch (Exception e) {

		}
		int listeningPort = server.getListeningPort();
		assertTrue(listeningPort > 0);
		assertTrue(server.getPort() != listeningPort);
		server.shutdown();
	}

	@Test
	public void testResetCallbackClient() {
		GatewayServer server = new GatewayServer(null, 0);
		server.start(true);
		try {
			Thread.sleep(250);
		} catch (Exception e) {

		}
		server.resetCallbackClient(server.getAddress(), GatewayServer.DEFAULT_PYTHON_PORT + 1);
		try {
			Thread.sleep(250);
		} catch (Exception e) {

		}
		int pythonPort = server.getPythonPort();
		InetAddress pythonAddress = server.getPythonAddress();
		assertEquals(pythonPort, GatewayServer.DEFAULT_PYTHON_PORT + 1);
		assertEquals(pythonAddress, server.getAddress());
		server.shutdown(true);
	}

	@Test
	public void testAuthentication() throws Exception {
		GatewayServer server = new GatewayServer.GatewayServerBuilder().authToken("secret").build();
		server.start(true);

		try {
			Socket valid = new Socket(server.getAddress(), server.getListeningPort());
			try {
				testServerAccess(valid, "secret");
			} finally {
				valid.close();
			}

			for (String invalidSecret : Arrays.asList("invalidSecret", null)) {
				Socket conn = new Socket(server.getAddress(), server.getListeningPort());
				try {
					testServerAccess(conn, invalidSecret);
					fail("Should have failed to communicate with server.");
				} catch (IOException ioe) {
					// Expected.
				} finally {
					conn.close();
				}
			}
		} finally {
			server.shutdown(true);
		}
	}

	private void testServerAccess(Socket s, String authToken) throws Exception {
		PrintWriter out = new PrintWriter(new OutputStreamWriter(s.getOutputStream(), "UTF-8"));
		BufferedReader in = new BufferedReader(new InputStreamReader(s.getInputStream(), "UTF-8"));

		if (authToken != null) {
			out.println(AuthCommand.COMMAND_NAME);
			out.println(authToken);
			out.flush();

			// Read the response from the auth request. Don't check it - let the rest of the test
			// make sure auth was successful or not.
			in.readLine();
		}

		// Send a "help" command and try to read the response. This should throw exceptions if
		// authentication fails.
		out.println(HelpPageCommand.HELP_COMMAND_NAME);
		out.println(HelpPageCommand.HELP_CLASS_SUB_COMMAND_NAME);
		out.println(HelpPageCommand.class.getName());
		out.println("");
		out.println("t");
		out.flush();

		String reply = in.readLine();
		if (authToken == null) {
			// If no auth token was provided, this code might be able to read a line of output before the
			// socket is closed by the server; it should be the error message from the auth check.
			assertEquals(Protocol.getOutputErrorCommand("Authentication error: unexpected command.").trim(), reply);

			// Throw an IOException since that's what the test above expects in this case.
			throw new IOException("Auth unsuccessful.");
		} else {
			assertTrue(Protocol.isReturnMessage(reply));
			if (Protocol.isError(reply.substring(1))) {
				throw new IOException("Error from server.");
			}
		}
	}

}

class TestListener implements GatewayServerListener {

	public List<Long> values = new CopyOnWriteArrayList<Long>();

	@Override
	public void serverStarted() {
		values.add(new Long(1));
	}

	@Override
	public void serverStopped() {
		values.add(new Long(10));
	}

	@Override
	public void serverError(Exception e) {
		values.add(new Long(100));
	}

	@Override
	public void serverPreShutdown() {
		values.add(new Long(1000));
	}

	@Override
	public void serverPostShutdown() {
		values.add(new Long(10000));
	}

	@Override
	public void connectionStarted(Py4JServerConnection gatewayConnection) {
		values.add(new Long(100000));
	}

	@Override
	public void connectionStopped(Py4JServerConnection gatewayConnection) {
		values.add(new Long(1000000));
	}

	@Override
	public void connectionError(Exception e) {
		values.add(new Long(10000000));
	}

}