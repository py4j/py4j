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

import java.io.IOException;
import java.net.InetAddress;
import java.net.Socket;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.logging.Logger;

import javax.net.SocketFactory;

import py4j.commands.Command;

/**
 * <p>
 * Subclass of CallbackClient that implements the new threading model,
 * ensuring that each thread uses its own connection.
 * </p>
 */
public class PythonClient extends CallbackClient {

	private Gateway gateway;

	private List<Class<? extends Command>> customCommands;

	protected final Logger logger = Logger.getLogger(PythonClient.class.getName());

	private Py4JJavaServer javaServer;

	public PythonClient(Gateway gateway, List<Class<? extends Command>> customCommands, int pythonPort,
			InetAddress pythonAddress, long minConnectionTime, TimeUnit minConnectionTimeUnit,
			SocketFactory socketFactory, Py4JJavaServer javaServer) {
		super(pythonPort, pythonAddress, minConnectionTime, minConnectionTimeUnit, socketFactory);
		this.gateway = gateway;
		this.javaServer = javaServer;
		this.customCommands = customCommands;
	}

	public Gateway getGateway() {
		return gateway;
	}

	public void setGateway(Gateway gateway) {
		this.gateway = gateway;
	}

	public Py4JJavaServer getJavaServer() {
		return javaServer;
	}

	public void setJavaServer(Py4JJavaServer javaServer) {
		this.javaServer = javaServer;
	}

	@Override
	protected void setupCleaner() {
		// Do nothing, we don't need a cleaner.
	}

	private Socket startClientSocket() throws IOException {
		logger.info("Starting Python Client connection on " + address + " at " + port);
		return socketFactory.createSocket(address, port);
	}

	@Override
	protected Py4JClientConnection getConnection() throws IOException {
		ClientServerConnection connection = null;

		connection = ClientServerConnection.getThreadConnection();
		if (connection == null || connection.getSocket() == null) {
			Socket socket = startClientSocket();
			connection = new ClientServerConnection(gateway, socket, customCommands, this, javaServer);
			connection.setInitiatedFromClient(true);
			connection.start();
			// TODO Need to test that we are not creating a leak.
			ClientServerConnection.setThreadConnection(connection);
			connections.addLast(connection);
		}

		return connection;
	}

	@Override
	protected boolean shouldRetrySendCommand(Py4JClientConnection cc, Py4JException pe) {
		boolean shouldRetry = false;

		if (cc instanceof ClientServerConnection) {
			ClientServerConnection csc = (ClientServerConnection) cc;
			shouldRetry = csc.isInitiatedFromClient();
		}

		return shouldRetry;
	}

	@Override
	protected void giveBackConnection(Py4JClientConnection cc) {
		// Do nothing because we already added the connection to the
		// connections deque
	}

	@Override
	public Py4JPythonClient copyWith(InetAddress pythonAddress, int pythonPort) {
		return new PythonClient(gateway, customCommands, pythonPort, pythonAddress, minConnectionTime,
				minConnectionTimeUnit, socketFactory, javaServer);
	}

}
