package net.sf.py4j.defaultserver;

import java.io.IOException;
import java.net.Socket;
import java.util.List;

import py4j.CallbackClient;
import py4j.Gateway;
import py4j.GatewayConnection;
import py4j.GatewayServer;
import py4j.commands.Command;

public class SWTGatewayServer extends GatewayServer {

	public SWTGatewayServer(Object entryPoint, int port, int pythonPort,
			int connectTimeout, int readTimeout,
			List<Class<? extends Command>> customCommands) {
		super(entryPoint, port, pythonPort, connectTimeout, readTimeout, customCommands);
	}

	public SWTGatewayServer(Object entryPoint, int port, int connectTimeout,
			int readTimeout, List<Class<? extends Command>> customCommands,
			CallbackClient cbClient) {
		super(entryPoint, port, connectTimeout, readTimeout, customCommands, cbClient);
	}

	public SWTGatewayServer(Object entryPoint, int port, int connectTimeout,
			int readTimeout) {
		super(entryPoint, port, connectTimeout, readTimeout);
	}

	public SWTGatewayServer(Object entryPoint, int port) {
		super(entryPoint, port);
	}

	public SWTGatewayServer(Object entryPoint) {
		super(entryPoint);
	}
	
	protected Object createConnection(Gateway gateway, Socket socket)
			throws IOException {
		return new SWTGatewayConnection(gateway, socket, customCommands, listeners);
	}


}
