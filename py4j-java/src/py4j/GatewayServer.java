/**
 * Copyright (c) 2009, Barthelemy Dagenais All rights reserved.
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

import java.net.ServerSocket;
import java.net.Socket;
import java.util.logging.Level;
import java.util.logging.Logger;

public class GatewayServer implements Runnable {

	public static final int DEFAULT_PORT = 25333;

	public static final int DEFAULT_CONNECT_TIMEOUT = 0;

	public static final int DEFAULT_READ_TIMEOUT = 0;

	private final int port;

	private final Gateway gateway;

	private final boolean acceptOnlyOne;

	private final int connect_timeout;

	private final int read_timeout;

	private final Logger logger = Logger.getLogger(GatewayServer.class
			.getName());

	private Socket currentSocket;

	private ServerSocket sSocket;

	public GatewayServer(Object entryPoint, int port, int connectTimeout,
			int readTimeout, boolean acceptOnlyOne) {
		super();
		this.gateway = new Gateway(entryPoint);
		this.port = port;
		connect_timeout = connectTimeout;
		read_timeout = readTimeout;
		this.acceptOnlyOne = acceptOnlyOne;
	}

	public GatewayServer(Object entryPoint) {
		this(entryPoint, DEFAULT_PORT, DEFAULT_CONNECT_TIMEOUT,
				DEFAULT_READ_TIMEOUT, false);
	}

	public GatewayServer(Object entryPoint, int port) {
		this(entryPoint, port, DEFAULT_CONNECT_TIMEOUT, DEFAULT_READ_TIMEOUT,
				false);
	}

	@Override
	public void run() {
		try {
			gateway.startup();
			sSocket = new ServerSocket(port);
			sSocket.setSoTimeout(connect_timeout);

			while (true) {
				Socket socket = sSocket.accept();
				processSocket(socket);
			}
		} catch (Exception e) {
			logger.log(Level.SEVERE, "Error while waiting for connection.", e);
		}
	}

	private void processSocket(Socket socket) {
		try {
			if (acceptOnlyOne && isConnected()) {
				socket.close();
			} else {
				socket.setSoTimeout(read_timeout);
				new GatewayConnection(this, gateway, socket);
				if (acceptOnlyOne) {
					currentSocket = socket;
				}
			}
		} catch (Exception e) {
			// Error while processing a connection should not be prevent the
			// gateway server from accepting new connections.
			logger
					.log(Level.WARNING, "Error while processing a connection.",
							e);
		}
	}

	private boolean isConnected() {
		return currentSocket != null && currentSocket.isConnected();
	}

	public void start(boolean fork) {
		if (fork) {
			Thread t = new Thread(this);
			t.start();
		} else {
			run();
		}
	}

	public void start() {
		start(true);
	}

	public void stop() {
		NetworkUtil.quietlyClose(sSocket);
		gateway.shutdown();
	}

	public boolean isAcceptOnlyOne() {
		return acceptOnlyOne;
	}

	public int getConnect_timeout() {
		return connect_timeout;
	}

	public int getRead_timeout() {
		return read_timeout;
	}

	public static void turnLoggingOff() {
		Logger.getLogger("py4j").setLevel(Level.OFF);
	}

	public static void turnLoggingOn() {
		Logger.getLogger("py4j").setLevel(Level.ALL);
	}
}
