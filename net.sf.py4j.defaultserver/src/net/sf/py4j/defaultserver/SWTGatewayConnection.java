package net.sf.py4j.defaultserver;

import java.io.IOException;
import java.net.Socket;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

import py4j.Gateway;
import py4j.GatewayConnection;
import py4j.GatewayServerListener;
import py4j.NetworkUtil;
import py4j.commands.CallCommand;
import py4j.commands.Command;

public class SWTGatewayConnection extends GatewayConnection {
	
	private final Logger logger = Logger.getLogger(SWTGatewayConnection.class.getName());

	public SWTGatewayConnection(Gateway gateway, Socket socket,
			List<Class<? extends Command>> customCommands,
			List<GatewayServerListener> listeners) throws IOException {
		super(gateway, socket, customCommands, listeners);
	}

	public SWTGatewayConnection(Gateway gateway, Socket socket)
			throws IOException {
		super(gateway, socket);
	}
	
	@Override
	public void run() {
		boolean executing = false;
		try {
			logger.info("Gateway Connection ready to receive messages");
			String commandLine = null;
			do {
				commandLine = reader.readLine();
				executing = true;
				logger.info("Received command: " + commandLine);
				final Command command = commands.get(commandLine);
				if (command != null) {
					// TODO Can cause deadlocks 
					// if this is an API command.
					if (!(command instanceof CallCommand)) {
						command.execute(commandLine, reader, writer);
					} else {
						final SWTCommand swtCommand = new SWTCommand(command);
						swtCommand.execute(commandLine, reader, writer);
					}
					executing = false;
				} else {
					logger.log(Level.WARNING, "Unknown command " + commandLine);
				}
			} while (commandLine != null && !commandLine.equals("q"));
		} catch (Throwable e) {
			logger.log(Level.WARNING,
					"Error occurred while waiting for a command.", e);
			if (executing && writer != null) {
				quietSendError(writer, e);
			}
		} finally {
			NetworkUtil.quietlyClose(socket);
			fireConnectionStopped();
		}
	}

}
