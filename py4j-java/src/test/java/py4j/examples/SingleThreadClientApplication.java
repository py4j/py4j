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
package py4j.examples;

import java.util.logging.ConsoleHandler;
import java.util.logging.Level;
import java.util.logging.Logger;

import py4j.ClientServer;
import py4j.GatewayServer;

public class SingleThreadClientApplication {

	public static void main(String[] args) {
		GatewayServer.turnAllLoggingOn();
		Logger logger = Logger.getLogger("py4j");
		logger.setLevel(Level.ALL);
		ConsoleHandler handler = new ConsoleHandler();
		handler.setLevel(Level.FINEST);
		logger.addHandler(handler);
		System.out.println("Starting");
		ClientServer clientServer = new ClientServer(null);
		IHello hello = (IHello) clientServer.getPythonServerEntryPoint(new Class[] { IHello.class });
		try {
			hello.sayHello();
			hello.sayHello(2, "Hello World");
		} catch (Exception e) {
			e.printStackTrace();
		}

		// This is to test connecting again if there was no successful
		// initial connection.
		//		try {
		//			Thread.currentThread().sleep(5000);
		//		} catch (Exception e) {
		//			e.printStackTrace();
		//		}
		//
		//		try {
		//			hello.sayHello();
		//			hello.sayHello(2, "Hello World");
		//		} catch (Exception e) {
		//			e.printStackTrace();
		//		}

		// This is to manually test reconnecting to the Python side after
		// graceful shutdown.
		//		clientServer.shutdown();
		//
		//		try {
		//			Thread.currentThread().sleep(1000);
		//		} catch (Exception e) {
		//			e.printStackTrace();
		//		}
		//
		//		clientServer = new ClientServer(null);
		//		hello = (IHello) clientServer.getPythonServerEntryPoint
		//				(new Class[] {IHello.class});
		//		hello.sayHello();
		//		hello.sayHello(2, "Hello World");
	}
}
