package py4j;

import py4j.commands.Command;

import javax.net.SocketFactory;
import java.io.IOException;
import java.net.InetAddress;
import java.net.Socket;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.logging.Logger;

/**
 * Created by barthelemy on 2016-02-12.
 */
public class PythonClient extends CallbackClient implements Py4JPythonClient {

	private Gateway gateway;

	private List<GatewayServerListener> listeners;

	private List<Class<? extends Command>> customCommands;

	protected final Logger logger = Logger.getLogger(PythonClient.class
			.getName());

	public PythonClient(Gateway gateway, List<Class<? extends Command>>
			customCommands, List<GatewayServerListener> listeners,
			int pythonPort, InetAddress
			pythonAddress, long minConnectionTime, TimeUnit
			minConnectionTimeUnit, SocketFactory socketFactory) {
		super(pythonPort, pythonAddress, minConnectionTime,
				minConnectionTimeUnit,
				socketFactory);
		this.gateway = gateway;
		this.listeners = listeners;
		this.customCommands = customCommands;
	}

	public Gateway getGateway() {
		return gateway;
	}

	public void setGateway(Gateway gateway) {
		this.gateway = gateway;
	}

	public List<GatewayServerListener> getListeners() {
		return listeners;
	}

	public void setListeners(List<GatewayServerListener> listeners) {
		this.listeners = listeners;
	}

	@Override
	protected void setupCleaner() {
		// Do nothing, we don't need a cleaner.
	}

	private Socket startClientSocket() throws IOException {
		logger.info("Starting Python Client connection on " + address + " at "
				+ port);
		return socketFactory.createSocket(address, port);
	}

	@Override
	protected Py4JClientConnection getConnection() throws IOException {
		Py4JClientConnection connection = null;

		connection = ClientServerConnection.getThreadConnection();
		if (connection == null) {
			Socket socket = startClientSocket();
			connection = new ClientServerConnection(
					gateway, socket, customCommands, listeners);
			connection.start();
			ClientServerConnection.setThreadConnection(
					(ClientServerConnection) connection);
			connections.addLast(connection);
		}

		return connection;
	}

	@Override
	protected void giveBackConnection(Py4JClientConnection cc) {
		// Do nothing because we already added the connection to the
		// connections deque
	}

	@Override
	public Py4JPythonClient copyWith(InetAddress pythonAddress, int pythonPort) {
		return new PythonClient(
				gateway,
				customCommands,
				listeners,
				pythonPort,
				pythonAddress,
				minConnectionTime,
				minConnectionTimeUnit,
				socketFactory);
	}

}
