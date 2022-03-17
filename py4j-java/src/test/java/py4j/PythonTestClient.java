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
package py4j;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;

public class PythonTestClient implements Runnable {

	public volatile String lastProxyMessage;
	public volatile String lastReturnMessage;
	public volatile String nextProxyReturnMessage;

	private ServerSocket sSocket;
	private volatile int port = 0;
	private volatile int pythonPort = 0;

	public void startProxy() {
		new Thread(this).start();
	}

	public void run() {
		try {
			sSocket = new ServerSocket(0);
			port = sSocket.getLocalPort();
			Socket socket = sSocket.accept();
			BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
			BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream()));
			lastProxyMessage = "";
			String temp = reader.readLine() + "\n";
			lastProxyMessage += temp;
			while (!temp.equals("e\n")) {
				temp = reader.readLine() + "\n";
				lastProxyMessage += temp;
			}
			writer.write(nextProxyReturnMessage);
			writer.flush();
			writer.close();
			reader.close();
			socket.close();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	public int getPort() {
		assert port != 0;
		return port;
	}

	public void setPythonPort(int port) {
		pythonPort = port;
	}

	public void stopProxy() {
		NetworkUtil.quietlyClose(sSocket);
	}

	public void sendMesage(String message) {
		try {
			Socket socket = new Socket(InetAddress.getByName(GatewayServer.DEFAULT_ADDRESS), pythonPort);
			BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
			BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream()));
			writer.write(message);
			writer.flush();
			lastReturnMessage = reader.readLine();
			writer.close();
			reader.close();
			socket.close();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

}
