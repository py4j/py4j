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

	private List<Class<? extends Command>> customCommands;

	protected final Logger logger = Logger.getLogger(PythonClient.class
			.getName());

	private Py4JJavaServer javaServer;

	public PythonClient(Gateway gateway, List<Class<? extends Command>>
			customCommands, int pythonPort, InetAddress pythonAddress,
			long minConnectionTime, TimeUnit minConnectionTimeUnit,
			SocketFactory socketFactory, Py4JJavaServer javaServer) {
		super(pythonPort, pythonAddress, minConnectionTime,
				minConnectionTimeUnit,
				socketFactory);
		this.gateway = gateway;
		this.javaServer = javaServer;
		this.customCommands = customCommands;
	}

	public Gateway getGateway() {
		return gateway;
	}

	public void setGateway(Gateway gateway) {
		this.gateway = gateway;
	}

	public Py4JJavaServer getJavaServer() {
		return javaServer;
	}

	public void setJavaServer(Py4JJavaServer javaServer) {
		this.javaServer = javaServer;
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
		ClientServerConnection connection = null;

		connection = ClientServerConnection.getThreadConnection();
		if (connection == null || connection.getSocket() == null) {
			Socket socket = startClientSocket();
			connection = new ClientServerConnection(
					gateway, socket, customCommands, this, javaServer);
			connection.setInitiatedFromClient(true);
			connection.start();
			// TODO Need to test that we are not creating a leak.
			ClientServerConnection.setThreadConnection(connection);
			connections.addLast(connection);
		}

		return connection;
	}

	@Override
	protected boolean shouldRetrySendCommand(Py4JClientConnection cc,
			Py4JException pe) {
		boolean shouldRetry = false;

		if (cc instanceof ClientServerConnection) {
			ClientServerConnection csc = (ClientServerConnection) cc;
			shouldRetry = csc.isInitiatedFromClient();
		}

		return shouldRetry;
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
				pythonPort,
				pythonAddress,
				minConnectionTime,
				minConnectionTimeUnit,
				socketFactory,
				javaServer);
	}

}
