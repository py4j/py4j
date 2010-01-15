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

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.Socket;
import java.nio.charset.Charset;
import java.util.HashMap;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;

public class GatewayConnection implements Runnable {

	@SuppressWarnings("unused")
	private final Gateway gateway;
	private final GatewayServer gatewayServer;
	private final Socket socket;
	private final BufferedWriter writer;
	private final BufferedReader reader;
	private final Map<String,Command> commands;
	private final Logger logger = Logger.getLogger(GatewayConnection.class.getName());
	
	public GatewayConnection(GatewayServer gatewayServer, Gateway gateway, Socket socket) throws IOException {
		super();
		this.gateway = gateway;
		this.gatewayServer = gatewayServer;
		this.socket = socket;
		this.reader = new BufferedReader(new InputStreamReader(socket.getInputStream(), Charset.forName("UTF-8")));
		this.writer = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream(), Charset.forName("UTF-8")));
		this.commands = new HashMap<String,Command>();
		initCommands(gateway);
		Thread t = new Thread(this);
		t.start();
	}
	
	/**
	 * <p>Override this method to initialize custom commands.</p>
	 * @param gateway
	 */
	protected void initCommands(Gateway gateway) {
		Command callCommand = new CallCommand();
		Command listCommand = new ListCommand();
		Command shutdownCommand = new ShutdownGatewayServerCommand(gatewayServer);
		callCommand.init(gateway);
		listCommand.init(gateway);
		shutdownCommand.init(gateway);
		commands.put(CallCommand.CALL_COMMAND_NAME,callCommand);
		commands.put(ListCommand.LIST_COMMAND_NAME,listCommand);
		commands.put(ShutdownGatewayServerCommand.SHUTDOWN_GATEWAY_SERVER_COMMAND_NAME,shutdownCommand);
	}
	
	
	@Override
	public void run() {
		try {
			String commandLine = null;
			do {
				commandLine = reader.readLine();
				logger.info("Received command: " + commandLine);
				Command command = commands.get(commandLine);
				if (command != null) {
					command.execute(commandLine, reader, writer);
				}
			} while (commandLine != null && !commandLine.equals('q'));
		} catch(Exception e) {
			logger.log(Level.WARNING, "Error occurred while waiting for a command.", e);
		} finally {
			logger.log(Level.INFO, "Closing connection.");
			NetworkUtil.quietlyClose(writer);
			NetworkUtil.quietlyClose(reader);
			NetworkUtil.quietlyClose(socket);
		}
	}

}
