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

public class GatewayServer {

	public static final int DEFAULT_PORT = 25333;
	
	public static final int DEFAULT_CONNECT_TIMEOUT = 0;
	
	public static final int DEFAULT_READ_TIMEOUT = 0;

	private int port = DEFAULT_PORT;

	private ServerSocket sSocket;

	private Gateway gateway = new ExampleGateway();

	private boolean acceptOnlyOne;
	
	private int connect_timeout = DEFAULT_CONNECT_TIMEOUT;
	
	private int read_timeout = DEFAULT_READ_TIMEOUT;

	public GatewayServer(Gateway gateway) {
		this.gateway = gateway;
	}

	public GatewayServer(Gateway gateway, int port) {
		this(gateway);
		this.port = port;
	}

	public void start() {
		try {
			gateway.startup();
			sSocket = new ServerSocket(port);
			sSocket.setSoTimeout(connect_timeout);
			while (true) {
				Socket socket = sSocket.accept();
				socket.setSoTimeout(read_timeout);
				new GatewayConnection(gateway, socket);
				if (acceptOnlyOne) {
					break;
				}
			}
		} catch (Exception e) {
			throw new Py4JException(e);
		}
	}
	
	public void stop() {
		gateway.shutdown();
	}

	public boolean isAcceptOnlyOne() {
		return acceptOnlyOne;
	}

	/**
	 * <p>
	 * Set to true to only accept one connection: useful for testing because the
	 * server does not stay up forever.
	 * </p>
	 * 
	 * <p>
	 * <b>TODO: ensure that we can shut down the server even if acceptOnlyOne is
	 * false!</b>
	 * </p>
	 * 
	 * @param acceptOnlyOne
	 */
	public void setAcceptOnlyOne(boolean acceptOnlyOne) {
		this.acceptOnlyOne = acceptOnlyOne;
	}

	public int getConnect_timeout() {
		return connect_timeout;
	}

	public void setConnect_timeout(int connectTimeout) {
		connect_timeout = connectTimeout;
	}

	public int getRead_timeout() {
		return read_timeout;
	}

	public void setRead_timeout(int readTimeout) {
		read_timeout = readTimeout;
	}
	
	public static void turnLoggingOff() {
		Logger.getLogger("py4j").setLevel(Level.OFF);
	}
	
	public static void turnLoggingOn() {
		Logger.getLogger("py4j").setLevel(Level.ALL);
	}
}
