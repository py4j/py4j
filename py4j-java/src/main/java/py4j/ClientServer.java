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

import java.net.InetAddress;
import java.util.concurrent.TimeUnit;
import java.util.logging.Logger;

import javax.net.ServerSocketFactory;
import javax.net.SocketFactory;

/**
 * <p>
 * This class creates the JavaServer and the PythonClient necessary to
 * communicate with a Python virtual machine with the new threading model.
 * </p>
 */
public class ClientServer {

	private final int javaPort;

	private final InetAddress javaAddress;

	private final int pythonPort;

	private final InetAddress pythonAddress;

	private int listeningPort;

	private final int connectTimeout;

	private final int readTimeout;

	private final ServerSocketFactory sSocketFactory;

	private final SocketFactory socketFactory;

	private final Gateway gateway;

	private final JavaServer javaServer;

	private final PythonClient pythonClient;

	protected final Logger logger = Logger.getLogger(ClientServer.class.getName());

	/**
	 *
	 * @param entryPoint
	 */
	public ClientServer(Object entryPoint) {
		this(GatewayServer.DEFAULT_PORT, GatewayServer.defaultAddress(), GatewayServer.DEFAULT_PYTHON_PORT,
				GatewayServer.defaultAddress(), GatewayServer.DEFAULT_CONNECT_TIMEOUT,
				GatewayServer.DEFAULT_READ_TIMEOUT, ServerSocketFactory.getDefault(), SocketFactory.getDefault(),
				entryPoint);
	}

	/**
	 *
	 * @param javaPort
	 * @param javaAddress
	 * @param pythonPort
	 * @param pythonAddress
	 * @param connectTimeout
	 * @param readTimeout
	 * @param sSocketFactory
	 * @param socketFactory
	 * @param entryPoint
	 */
	public ClientServer(int javaPort, InetAddress javaAddress, int pythonPort, InetAddress pythonAddress,
			int connectTimeout, int readTimeout, ServerSocketFactory sSocketFactory, SocketFactory socketFactory,
			Object entryPoint) {
		this.javaPort = javaPort;
		this.javaAddress = javaAddress;
		this.pythonPort = pythonPort;
		this.pythonAddress = pythonAddress;
		this.connectTimeout = connectTimeout;
		this.readTimeout = readTimeout;
		this.sSocketFactory = sSocketFactory;
		this.socketFactory = socketFactory;

		this.pythonClient = new PythonClient(null, null, pythonPort, pythonAddress,
				CallbackClient.DEFAULT_MIN_CONNECTION_TIME, TimeUnit.SECONDS, SocketFactory.getDefault(), null);
		this.javaServer = new JavaServer(entryPoint, this.javaPort, this.connectTimeout, this.readTimeout, null,
				pythonClient);
		this.gateway = javaServer.getGateway();
		pythonClient.setGateway(gateway);
		pythonClient.setJavaServer(javaServer);
		// XXX Force gateway startup here
		this.gateway.startup();
	}

	public Py4JJavaServer getJavaServer() {
		return javaServer;
	}

	public Py4JPythonClient getPythonClient() {
		return pythonClient;
	}

	/**
	 * <p>
	 * Starts the JavaServer, which will handle requests from the Python side.
	 * </p>
	 *
	 * @param fork If the JavaServer is started in this thread or in its own
	 *                thread.
	 */
	public void startServer(boolean fork) {
		javaServer.start(fork);
	}

	/**
	 * Shuts down the Java Server so that it stops accepting requests and it
	 * closes existing connections.
	 */
	public void shutdown() {
		this.javaServer.shutdown(true);
	}

	/**
	 * <p>
	 * Gets a reference to the entry point on the Python side. This is often
	 * necessary if Java is driving the communication because Java cannot call
	 * static methods, initialize Python objects or load Python modules yet.
	 * </p>
	 *
	 * @param interfacesToImplement
	 * @return
	 */
	public Object getPythonServerEntryPoint(Class[] interfacesToImplement) {
		Object proxy = Protocol.getPythonProxyHandler(gateway.getClass().getClassLoader(), interfacesToImplement,
				Protocol.ENTRY_POINT_OBJECT_ID, gateway);
		return proxy;
	}

}
