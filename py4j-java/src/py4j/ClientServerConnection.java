package py4j;

import py4j.commands.Command;

import java.io.*;
import java.net.Socket;
import java.nio.charset.Charset;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Created by barthelemy on 2016-02-12.
 */
public class ClientServerConnection implements Py4JServerConnection,
		Py4JClientConnection, Runnable {

	private boolean used = false;
	private static ThreadLocal<ClientServerConnection> threadConnections =
			new ThreadLocal<ClientServerConnection>();
	protected final Socket socket;
	protected final BufferedWriter writer;
	protected final BufferedReader reader;
	protected final Map<String, Command> commands;
	protected final Logger logger = Logger.getLogger(
			ClientServerConnection.class.getName());
	protected final List<GatewayServerListener> listeners;

	public ClientServerConnection(Gateway gateway, Socket socket,
			List<Class<? extends Command>> customCommands,
			List<GatewayServerListener> listeners) throws IOException {
		super();
		this.socket = socket;
		this.reader = new BufferedReader(new InputStreamReader(
				socket.getInputStream(), Charset.forName("UTF-8")));
		this.writer = new BufferedWriter(new OutputStreamWriter(
				socket.getOutputStream(), Charset.forName("UTF-8")));
		this.commands = new HashMap<String, Command>();
		initCommands(gateway, GatewayConnection.getBaseCommands());
		if (customCommands != null) {
			initCommands(gateway, customCommands);
		}
		this.listeners = listeners;
	}


	public void startServerConnection() {
		Thread t = new Thread(this);
		t.start();
	}

	public static ClientServerConnection getThreadConnection() {
		return threadConnections.get();
	}

	public static void setThreadConnection(ClientServerConnection
			clientServerConnection) {
		threadConnections.set(clientServerConnection);
	}

	public void run() {
		setThreadConnection(this);
		waitForCommands();
	}

	/**
	 * <p>
	 * Override this method to initialize custom commands.
	 * </p>
	 *
	 * @param gateway
	 */
	protected void initCommands(Gateway gateway,
			List<Class<? extends Command>> commandsClazz) {
		for (Class<? extends Command> clazz : commandsClazz) {
			try {
				Command cmd = clazz.newInstance();
				cmd.init(gateway);
				commands.put(cmd.getCommandName(), cmd);
			} catch (Exception e) {
				String name = "null";
				if (clazz != null) {
					name = clazz.getName();
				}
				logger.log(Level.SEVERE,
						"Could not initialize command " + name, e);
			}
		}
	}

	protected void fireConnectionStopped() {
		logger.info("Connection Stopped");

		for (GatewayServerListener listener : listeners) {
			try {
				listener.connectionStopped(this);
			} catch (Exception e) {
				logger.log(Level.SEVERE, "A listener crashed.", e);
			}
		}
	}

	protected void quietSendError(BufferedWriter writer, Throwable exception) {
		try {
			String returnCommand = Protocol.getOutputErrorCommand(exception);
			logger.fine("Trying to return error: " + returnCommand);
			writer.write(returnCommand);
			writer.flush();
		} catch (Exception e) {

		}
	}

	@Override
	public Socket getSocket() {
		return socket;
	}

	public void waitForCommands() {
		boolean executing = false;
		try {
			logger.info("Gateway Connection ready to receive messages");
			String commandLine = null;
			do {
				commandLine = reader.readLine();
				executing = true;
				logger.fine("Received command: " + commandLine);
				Command command = commands.get(commandLine);
				if (command != null) {
					command.execute(commandLine, reader, writer);
					executing = false;
				} else {
					logger.log(Level.WARNING, "Unknown command " + commandLine);
					// TODO SEND BACK AN ERROR?
				}
			} while (commandLine != null && !commandLine.equals("q"));
		} catch (Exception e) {
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

	public String sendCommand(String command) {
		return this.sendCommand(command, true);
	}

	public String sendCommand(String command, boolean blocking) {
		// TODO REFACTOR so that we use the same code in sendCommand and wait
		logger.log(Level.INFO, "Sending Python command: " + command);
		String returnCommand = null;
		try {
			writer.write(command);
			writer.flush();

			while (true) {
				if (blocking) {
					returnCommand = this.readBlockingResponse(this.reader);
				} else {
					returnCommand = this.readNonBlockingResponse(this.socket, this
							.reader);
				}

				if (returnCommand == null || returnCommand.trim().equals("")) {
					// TODO LOG AND DO SOMETHING INTELLIGENT
					throw new Py4JException("Received empty command");
				} else if (Protocol.isReturnMessage(returnCommand)) {
					returnCommand = returnCommand.substring(1);
					logger.log(Level.INFO, "Returning CB command: " + returnCommand);
					return returnCommand;
				} else {
					Command commandObj = commands.get(returnCommand);
					if (commandObj != null) {
						commandObj.execute(returnCommand, reader, writer);
					} else {
						logger.log(Level.WARNING, "Unknown command " + returnCommand);
						// TODO SEND BACK AN ERROR?
					}
				}

			}
		} catch (Exception e) {
			throw new Py4JNetworkException("Error while sending a command: "
					+ command, e);
		}
	}

	@Override
	public void shutdown() {
		NetworkUtil.quietlyClose(reader);
		NetworkUtil.quietlyClose(writer);
		NetworkUtil.quietlyClose(socket);
	}

	@Override
	public void start() throws IOException {

	}

	@Override
	public void setUsed(boolean used) {
		this.used = used;
	}

	@Override
	public boolean wasUsed() {
		return used;
	}

	protected String readBlockingResponse(BufferedReader reader) throws
			IOException {
		return reader.readLine();
	}

	protected String readNonBlockingResponse(Socket socket, BufferedReader
			reader)
			throws IOException {
		String returnCommand = null;

		socket.setSoTimeout(CallbackConnection.DEFAULT_NONBLOCKING_SO_TIMEOUT);

		while (true) {
			try {
				returnCommand = reader.readLine();
				break;
			} finally {
				// Set back blocking timeout (necessary if
				// sockettimeoutexception is raised and propagated)
				socket.setSoTimeout(0);
			}
		}

		// Set back blocking timeout
		socket.setSoTimeout(0);

		return returnCommand;
	}
}
