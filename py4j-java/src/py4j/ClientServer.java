package py4j;

import py4j.commands.Command;

import javax.net.ServerSocketFactory;
import javax.net.SocketFactory;
import java.io.*;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.charset.Charset;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Created by barthelemy on 2016-02-09.
 */
public class ClientServer implements Py4JServer, Py4JClient {

	private final int javaPort;

	private final InetAddress javaAddress;

	private final int pythonPort;

	private final InetAddress pythonAddress;

	private int listeningPort;

	private final int connectTimeout;

	private final int readTimeout;

	private final ServerSocketFactory sSocketFactory;

	private final SocketFactory socketFactory;

	private final Gateway gateway;

	private ServerSocket sSocket;

	protected Socket socket;

	protected BufferedWriter writer;

	protected BufferedReader reader;

	protected final Map<String, Command> commands;

	protected final Logger logger = Logger.getLogger(ClientServer.class
			.getName());


	public ClientServer(Object entryPoint) {
		this.javaPort = GatewayServer.DEFAULT_PORT;
		this.javaAddress = GatewayServer.defaultAddress();
		this.pythonPort = GatewayServer.DEFAULT_PYTHON_PORT;
		this.pythonAddress = GatewayServer.defaultAddress();
		this.connectTimeout = GatewayServer.DEFAULT_CONNECT_TIMEOUT;
		this.readTimeout = GatewayServer.DEFAULT_READ_TIMEOUT;
		this.sSocketFactory = ServerSocketFactory.getDefault();
		this.socketFactory = SocketFactory.getDefault();
		this.gateway = new Gateway(entryPoint, this);
		this.gateway.getBindings().put(GatewayServer.GATEWAY_SERVER_ID, this);
		this.commands = new HashMap<String, Command>();
		initCommands(gateway, GatewayConnection.getBaseCommands());
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
	public void shutdown() {
		// TODO
		System.out.println("SHOULD SHUT DOWN");
	}

	public void startServer() {
		try {
			gateway.startup();
			sSocket = sSocketFactory.createServerSocket(javaPort, -1, javaAddress);
			sSocket.setSoTimeout(connectTimeout);
			sSocket.setReuseAddress(true);
			socket = sSocket.accept();
			logger.info("Client socket accepted.");
			socket.setSoTimeout(readTimeout);
			reader = new BufferedReader(new InputStreamReader(
					socket.getInputStream(), Charset.forName("UTF-8")));
			writer = new BufferedWriter(new OutputStreamWriter(
					socket.getOutputStream(), Charset.forName("UTF-8")));
		} catch(IOException e) {
			throw new Py4JNetworkException(e);
		}
		waitForCommands();
	}

	public void startClient() {
		gateway.startup();
		try {
			socket = socketFactory.createSocket(pythonAddress, pythonPort);
			reader = new BufferedReader(new InputStreamReader(
					socket.getInputStream(), Charset.forName("UTF-8")));
			writer = new BufferedWriter(new OutputStreamWriter(
					socket.getOutputStream(), Charset.forName("UTF-8")));
		} catch(IOException e) {
			throw new Py4JNetworkException(e);
		}
	}

	@Override
	public String sendCommand(String command) {
		return this.sendCommand(command, true);
	}

	@Override
	public String sendCommand(String command, boolean blocking) {
		if (socket == null) {
			startClient();
		}
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

	@Override
	public Py4JClient copyWith(InetAddress pythonAddress, int pythonPort) {
		throw new UnsupportedOperationException();
	}

	public Object getPythonServerEntryPoint(Class[] interfacesToImplement) {
		Object proxy = Protocol.getPythonProxyHandler(gateway.getClass()
				.getClassLoader(), interfacesToImplement, Protocol.ENTRY_POINT_OBJECT_ID,
				gateway);
		return proxy;
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
			//fireConnectionStopped();
		}
	}

}
