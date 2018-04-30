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
package py4j.examples;

import javax.net.SocketFactory;

import py4j.CallbackClient;
import py4j.GatewayServer;

public class ExampleApplication {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		GatewayServer.turnLoggingOff();
		GatewayServer server = new GatewayServer(new ExampleEntryPoint());
		server.start();
	}

	public static class ExampleNoMemManagementApplication {
		public static void main(String[] args) {
			GatewayServer.turnLoggingOff();
			CallbackClient callbackClient = new CallbackClient(GatewayServer.DEFAULT_PYTHON_PORT,
					GatewayServer.defaultAddress(), CallbackClient.DEFAULT_MIN_CONNECTION_TIME,
					CallbackClient.DEFAULT_MIN_CONNECTION_TIME_UNIT, SocketFactory.getDefault(), false);
			GatewayServer server = new GatewayServer(new ExampleEntryPoint(), GatewayServer.DEFAULT_PORT,
					GatewayServer.defaultAddress(), GatewayServer.DEFAULT_CONNECT_TIMEOUT,
					GatewayServer.DEFAULT_READ_TIMEOUT, null, callbackClient);
			server.start();
		}
	}

	public static class ExamplePythonEntryPointApplication {

		public static void main(String[] args) {
			String authToken = null;
			if (args.length > 0) {
				authToken = args[0];
			}
			GatewayServer.turnLoggingOff();
			GatewayServer server = new GatewayServer.GatewayServerBuilder()
					.callbackClient(GatewayServer.DEFAULT_PYTHON_PORT, GatewayServer.defaultAddress(), authToken)
					.build();
			server.start();
			IHello hello = (IHello) server.getPythonServerEntryPoint(new Class[] { IHello.class });
			try {
				hello.sayHello();
				hello.sayHello(2, "Hello World");
			} catch (Exception e) {
				e.printStackTrace();
			}
		}
	}

	public static class ExampleShortTimeoutApplication {
		public static void main(String[] args) {
			GatewayServer.turnLoggingOff();
			CallbackClient callbackClient = new CallbackClient(GatewayServer.DEFAULT_PYTHON_PORT,
					GatewayServer.defaultAddress(), CallbackClient.DEFAULT_MIN_CONNECTION_TIME,
					CallbackClient.DEFAULT_MIN_CONNECTION_TIME_UNIT, SocketFactory.getDefault(), false, 250);
			GatewayServer server = new GatewayServer.GatewayServerBuilder().readTimeout(250)
					.entryPoint(new ExampleEntryPoint()).callbackClient(callbackClient).build();
			server.start();

		}
	}

	public static class ExampleIPv6Application {
		public static void main(String[] args) {
			GatewayServer.turnLoggingOff();
			CallbackClient callbackClient = new CallbackClient(GatewayServer.DEFAULT_PYTHON_PORT,
					GatewayServer.defaultIPv6Address(), CallbackClient.DEFAULT_MIN_CONNECTION_TIME,
					CallbackClient.DEFAULT_MIN_CONNECTION_TIME_UNIT, SocketFactory.getDefault(), false, 250);
			GatewayServer server = new GatewayServer.GatewayServerBuilder().readTimeout(250)
					.entryPoint(new ExampleEntryPoint()).callbackClient(callbackClient)
					.javaAddress(GatewayServer.defaultIPv6Address()).build();
			server.start();

		}
	}

}
