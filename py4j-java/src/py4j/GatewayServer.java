/**
 * Copyright (c) 2009, 2010, Barthelemy Dagenais All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 * 
 * - Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
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
 */

package py4j;

import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

import py4j.commands.Command;

/**
 * <p>
 * This class enables Python programs to access a Java program. When a
 * GatewayServer instance is started, Python programs can connect to the JVM by
 * calling:
 * </p>
 * 
 * <p>
 * <code>gateway = JavaGateway()</code>
 * </p>
 * 
 * <p>
 * The
 * <code>entryPoint</entry> passed to a GatewayServer can be accessed with the <code>entry_point</code>
 * member:
 * </p>
 * 
 * <p>
 * <code>gateway.entry_point</code>
 * </p>
 * 
 * <p>
 * Technically, a GatewayServer is only responsible for accepting connection.
 * Each connection is then handled by a {@link py4j.GatewayConnection
 * GatewayConnection} instance and the various states (e.g., entryPoint,
 * reference to returned objects) are managed by a {@link py4j.Gateway Gateway}
 * instance.
 * </p>
 * 
 * @author Barthelemy Dagenais
 * 
 */
public class GatewayServer implements Runnable {

	public static final int DEFAULT_PORT = 25333;

	public static final int DEFAULT_PYTHON_PORT = 25334;

	public static final int DEFAULT_CONNECT_TIMEOUT = 0;

	public static final int DEFAULT_READ_TIMEOUT = 0;

	public static final String GATEWAY_SERVER_ID = "GATEWAY_SERVER";

	private final int port;

	private final int pythonPort;

	private final Gateway gateway;

	private final int connectTimeout;

	private final int readTimeout;

	private final Logger logger = Logger.getLogger(GatewayServer.class
			.getName());

	private final List<Socket> connections = new ArrayList<Socket>();

	private final CallbackClient cbClient;

	private final List<Class<? extends Command>> customCommands;

	private ServerSocket sSocket;

	static {
		GatewayServer.turnLoggingOff();
	}

	/**
	 * 
	 * @param entryPoint
	 *            The entry point of this Gateway. Can be null.
	 * @param port
	 *            The port the GatewayServer is listening to.
	 * @param connectTimeout
	 *            Time in milliseconds (0 = infinite). If a GatewayServer does
	 *            not receive a connection request after this time, it closes
	 *            the server socket and no other connection is accepted.
	 * @param readTimeout
	 *            Time in milliseconds (0 = infinite). Once a Python program is
	 *            connected, if a GatewayServer does not receive a request
	 *            (e.g., a method call) after this time, the connection with the
	 *            Python program is closed.
	 */
	public GatewayServer(Object entryPoint, int port, int connectTimeout,
			int readTimeout) {
		this(entryPoint, port, DEFAULT_PYTHON_PORT, connectTimeout,
				readTimeout, null);
	}

	/**
	 * 
	 * @param entryPoint
	 *            The entry point of this Gateway. Can be null.
	 * @param port
	 *            The port the GatewayServer is listening to.
	 * @param pythonPort
	 *            The port used by a PythonProxyHandler to connect to a Python
	 *            gateway. Essentially the port used for Python callbacks.
	 * @param connectTimeout
	 *            Time in milliseconds (0 = infinite). If a GatewayServer does
	 *            not receive a connection request after this time, it closes
	 *            the server socket and no other connection is accepted.
	 * @param readTimeout
	 *            Time in milliseconds (0 = infinite). Once a Python program is
	 *            connected, if a GatewayServer does not receive a request
	 *            (e.g., a method call) after this time, the connection with the
	 *            Python program is closed.
	 * @param customCommands
	 *            A list of custom Command classes to augment the Server
	 *            features. These commands will be accessible from Python
	 *            programs. Can be null.
	 */
	public GatewayServer(Object entryPoint, int port, int pythonPort,
			int connectTimeout, int readTimeout,
			List<Class<? extends Command>> customCommands) {
		super();
		this.port = port;
		this.pythonPort = pythonPort;
		this.connectTimeout = connectTimeout;
		this.readTimeout = readTimeout;
		this.cbClient = new CallbackClient(pythonPort);
		this.gateway = new Gateway(entryPoint, cbClient);
		this.gateway.getBindings().put(GATEWAY_SERVER_ID, this);
		this.customCommands = customCommands;
	}
	
	public GatewayServer(Object entryPoint, int port, int connectTimeout, int readTimeout, List<Class<? extends Command>> customCommands, CallbackClient cbClient) {
		super();
		this.port = port;
		this.connectTimeout = connectTimeout;
		this.readTimeout = readTimeout;
		this.cbClient = cbClient;
		this.pythonPort = cbClient.getPort();
		this.gateway = new Gateway(entryPoint, cbClient);
		this.gateway.getBindings().put(GATEWAY_SERVER_ID, this);
		this.customCommands = customCommands;
	}

	/**
	 * <p>
	 * Creates a GatewayServer instance with default port (25333), default
	 * address (localhost), and default timeout value (no timeout).
	 * </p>
	 * 
	 * @param entryPoint
	 *            The entry point of this Gateway. Can be null.
	 */
	public GatewayServer(Object entryPoint) {
		this(entryPoint, DEFAULT_PORT, DEFAULT_CONNECT_TIMEOUT,
				DEFAULT_READ_TIMEOUT);
	}

	/**
	 * 
	 * @param entryPoint
	 *            The entry point of this Gateway. Can be null.
	 * @param port
	 *            The port the GatewayServer is listening to.
	 */
	public GatewayServer(Object entryPoint, int port) {
		this(entryPoint, port, DEFAULT_CONNECT_TIMEOUT, DEFAULT_READ_TIMEOUT);
	}

	@Override
	public void run() {
		try {
			logger.info("Gateway Server Starting");
			gateway.startup();
			sSocket = new ServerSocket(port);
			sSocket.setSoTimeout(connectTimeout);

			while (true) {
				Socket socket = sSocket.accept();
				processSocket(socket);
			}
		} catch (Exception e) {
			logger.log(Level.SEVERE, "Error while waiting for connection.", e);
		}
		logger.info("Gateway Server Stopping");
	}

	protected Object createConnection(Gateway gateway, Socket socket)
			throws IOException {
		return new GatewayConnection(gateway, socket, customCommands);
	}

	private void processSocket(Socket socket) {
		try {
			logger.info("Gateway Server accepted a connection");
			connections.add(socket);
			socket.setSoTimeout(readTimeout);
			createConnection(gateway, socket);
		} catch (Exception e) {
			// Error while processing a connection should not be prevent the
			// gateway server from accepting new connections.
			logger.log(Level.WARNING, "Error while processing a connection.", e);
		}
	}

	/**
	 * <p>
	 * Starts to accept connections.
	 * </p>
	 * 
	 * @param fork
	 *            If true, the GatewayServer accepts connection in another
	 *            thread and this call is non-blocking. If False, the
	 *            GatewayServer accepts connection in this thread and the call
	 *            is blocking (until the Gateway is shutdown by another thread).
	 */
	public void start(boolean fork) {
		if (fork) {
			Thread t = new Thread(this);
			t.start();
		} else {
			run();
		}
	}

	/**
	 * <p>
	 * Starts to accept connections in a second thread (non-blocking call).
	 * </p>
	 */
	public void start() {
		start(true);
	}

	/**
	 * <p>
	 * Stops accepting connections, closes all current connections, and calls
	 * {@link py4j.Gateway#shutdown() Gateway.shutdown()}
	 * </p>
	 */
	public void shutdown() {
		logger.info("Shutting down Gateway");
		// TODO Check that all connections are indeed closed!
		NetworkUtil.quietlyClose(sSocket);
		for (Socket socket : connections) {
			NetworkUtil.quietlyClose(socket);
		}
		connections.clear();
		gateway.shutdown();
		cbClient.shutdown();
	}

	public int getConnectTimeout() {
		return connectTimeout;
	}

	public int getReadTimeout() {
		return readTimeout;
	}

	public int getPythonPort() {
		return pythonPort;
	}

	public CallbackClient getCallbackClient() {
		return cbClient;
	}

	/**
	 * <p>
	 * Utility method to turn logging off. Logging is turned off by default.
	 * </p>
	 */
	public static void turnLoggingOff() {
		Logger.getLogger("py4j").setLevel(Level.OFF);
	}

	/**
	 * <p>
	 * Utility method to turn logging on. Logging is turned off by default.
	 * </p>
	 */
	public static void turnLoggingOn() {
		Logger.getLogger("py4j").setLevel(Level.ALL);
	}
}
