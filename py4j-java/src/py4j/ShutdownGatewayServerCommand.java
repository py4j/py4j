/*******************************************************************************
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
 *******************************************************************************/
package py4j;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;

/**
 * <p>
 * The ShutdownGatewayServerCommand is responsible for shutting down the
 * GatewayServer. This command is useful to shut down the server remotely, i.e.,
 * from the Python side.
 * </p>
 * 
 * @author Barthelemy Dagenais
 * 
 */
public class ShutdownGatewayServerCommand extends AbstractCommand {

	private GatewayServer gatewayServer;

	public static final String SHUTDOWN_GATEWAY_SERVER_COMMAND_NAME = "s";

	public ShutdownGatewayServerCommand() {
		super();
		this.commandName = SHUTDOWN_GATEWAY_SERVER_COMMAND_NAME;
	}

	@Override
	public void init(Gateway gateway) {
		super.init(gateway);
		this.gatewayServer = (GatewayServer) gateway.getObject(GatewayServer.GATEWAY_SERVER_ID);
	}

	@Override
	public void execute(String commandName, BufferedReader reader,
			BufferedWriter writer) throws Py4JException, IOException {
		this.gatewayServer.shutdown();
	}

}
