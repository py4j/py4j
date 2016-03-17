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

import java.io.FileNotFoundException;
import java.io.InputStream;
import java.net.InetAddress;
import java.security.KeyStore;
import java.util.concurrent.TimeUnit;

import javax.net.ssl.KeyManagerFactory;
import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManagerFactory;

import py4j.CallbackClient;
import py4j.GatewayServer;

// import java.util.logging.Level;
// import java.util.logging.Logger;

public class ExampleSSLApplication {

	/**
	 * @see "http://stackoverflow.com/a/34483734/42543"
	 */
	public static void main(String[] args) throws Exception {
		SSLContext sslContext = SSLContext.getInstance("TLS");

		char[] password = "password".toCharArray();
		KeyStore ks = KeyStore.getInstance("JKS");
		InputStream fis = ExampleSSLApplication.class.getClassLoader().getResourceAsStream("selfsigned.jks");
		if (fis == null) {
			throw new FileNotFoundException("expected a 'selfsigned.jks' keystore on the classpath");
		}
		ks.load(fis, password);

		// setup the key manager factory
		KeyManagerFactory kmf = KeyManagerFactory.getInstance("SunX509");
		kmf.init(ks, password);

		// setup the trust manager factory
		TrustManagerFactory tmf = TrustManagerFactory.getInstance("SunX509");
		tmf.init(ks);

		// setup the HTTPS context and parameters
		sslContext.init(kmf.getKeyManagers(), tmf.getTrustManagers(), null);

		GatewayServer.turnLoggingOff();
		// Logger logger = Logger.getLogger("py4j");
		// logger.setLevel(Level.ALL);

		GatewayServer server = new GatewayServer(new ExampleEntryPoint(), GatewayServer.DEFAULT_PORT,
				InetAddress.getByName("localhost"), GatewayServer.DEFAULT_CONNECT_TIMEOUT,
				GatewayServer.DEFAULT_READ_TIMEOUT, null,
				new CallbackClient(GatewayServer.DEFAULT_PYTHON_PORT,
						InetAddress.getByName(CallbackClient.DEFAULT_ADDRESS),
						CallbackClient.DEFAULT_MIN_CONNECTION_TIME, TimeUnit.SECONDS, sslContext.getSocketFactory()),
				sslContext.getServerSocketFactory());
		server.start();
	}

}
