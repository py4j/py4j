package net.sf.py4j.defaultserver;

import java.io.IOException;
import java.net.Socket;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

import org.eclipse.swt.widgets.Display;

import py4j.Gateway;
import py4j.GatewayConnection;
import py4j.GatewayServerListener;
import py4j.NetworkUtil;
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
				final String  cmdLine = commandLine;
				final List<Throwable> errors = new ArrayList<Throwable>(1);
				if (command != null) {
					Display.getDefault().syncExec(new Runnable() {
						public void run() {
							try {
							    command.execute(cmdLine, reader, writer);
							} catch (Throwable ne) {
								errors.add(ne);
							}
						}
					});
					if (!errors.isEmpty()) throw errors.get(0);
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
