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
package py4j.instrumented;

import java.io.IOException;
import java.net.Socket;

import py4j.Gateway;
import py4j.GatewayServer;
import py4j.Py4JServerConnection;

public class InstrGatewayServer extends GatewayServer {

	public InstrGatewayServer(Object entryPoint, int port, int pythonPort) {
		super(entryPoint, port, DEFAULT_CONNECT_TIMEOUT, DEFAULT_READ_TIMEOUT, null,
				new InstrCallbackClient(pythonPort));
		MetricRegistry.addCreatedObject(this);
	}

	@Override
	protected void finalize() throws Throwable {
		MetricRegistry.addFinalizedObject(this);
		super.finalize();
	}

	/**
	 * <p>
	 * Creates a server connection from a Python call to the Java side.
	 * </p>
	 *
	 * @param gateway
	 * @param socket
	 * @return
	 * @throws IOException
	 */
	protected Py4JServerConnection createConnection(Gateway gateway, Socket socket) throws IOException {
		InstrGatewayConnection connection = new InstrGatewayConnection(gateway, socket, getCustomCommands(),
				getListeners());
		connection.startConnection();
		return connection;
	}
}
