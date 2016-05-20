/******************************************************************************
 * Copyright (c) 2009-2016, Barthelemy Dagenais and individual contributors.
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
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public class ClientServerTest {

	@Test
	public void testListenerClientServer() {
		TestListener listener = new TestListener();
		ClientServer server1 = new ClientServer(null);
		Py4JJavaServer javaServer = server1.getJavaServer();
		javaServer.addListener(listener);
		server1.startServer(true);
		try {
			Thread.sleep(250);
		} catch (Exception e) {

		}
		server1.shutdown();
		try {
			Thread.sleep(250);
		} catch (Exception e) {

		}
		// Started, PreShutdown, Error, Stopped, PostShutdown
		// But order cannot be guaranteed because two threads are competing.
		assertTrue(listener.values.contains(new Long(1)));
		assertTrue(listener.values.contains(new Long(10)));
		assertTrue(listener.values.contains(new Long(100)));
		assertTrue(listener.values.contains(new Long(1000)));
		assertTrue(listener.values.contains(new Long(10000)));
		assertEquals(5, listener.values.size());
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
		int listeningPort = ((GatewayServer) javaServer).getListeningPort();
		assertTrue(listeningPort > 0);
		assertTrue(((GatewayServer) javaServer).getPort() != listeningPort);
		server.shutdown();
	}
}
