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
package py4j.commands;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.fail;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.StringReader;
import java.io.StringWriter;
import java.util.concurrent.CountDownLatch;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import py4j.Gateway;
import py4j.GatewayServer;
import py4j.Py4JJavaServer;

public class CancelCommandTest {
	private Gateway gateway;
	private BufferedWriter writer;
	private StringWriter sWriter;

	@Before
	public void setUp() {
		gateway = new Gateway(null);
		gateway.startup();
		sWriter = new StringWriter();
		writer = new BufferedWriter(sWriter);
	}

	@After
	public void tearDown() {
		gateway.shutdown();
	}

	@Test
	public void testCancelCommandGatewayServerIsNull() {
		try {
			gateway.deleteObject(GatewayServer.GATEWAY_SERVER_ID);
			CancelCommand command = new CancelCommand();
			command.init(gateway, null);
			// Should not fail with NullPointerException.
			command.execute("z", new BufferedReader(new StringReader("address\n1000\n2000")), writer);
			assertNull(gateway.getObject(GatewayServer.GATEWAY_SERVER_ID));
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testCancelCommand() {
		try {
			final CountDownLatch latch = new CountDownLatch(1);
			Py4JJavaServer server = new GatewayServer() {
				@Override
				public void shutdownSocket(String address, int remotePort, int localPort) {
					assertEquals(address, "address");
					assertEquals(remotePort, 1000);
					assertEquals(localPort, 2000);
					latch.countDown();
				}
			};
			gateway.getBindings().put(GatewayServer.GATEWAY_SERVER_ID, server);
			CancelCommand command = new CancelCommand();
			command.init(gateway, null);
			command.execute("z", new BufferedReader(new StringReader("address\n1000\n2000")), writer);
			latch.await();
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
}
