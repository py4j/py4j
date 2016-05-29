package py4j.instrumented;

import py4j.Gateway;
import py4j.GatewayServer;
import py4j.Py4JServerConnection;

import java.io.IOException;
import java.net.Socket;

public class InstrGatewayServer  extends GatewayServer {

	public InstrGatewayServer(Object entryPoint, int port, int pythonPort) {
		super(entryPoint, port, DEFAULT_CONNECT_TIMEOUT, DEFAULT_READ_TIMEOUT, null, new InstrCallbackClient(pythonPort));
		MetricRegistry.addCreatedObject(this);
	}

	@Override protected void finalize() throws Throwable {
		MetricRegistry.addFinalizedObject(this);
		super.finalize();
	}

	/**
	 * <p>
	 * Creates a server connection from a Python call to the Java side.
	 * </p>
	 *
	 * @param gateway
	 * @param socket
	 * @return
	 * @throws IOException
	 */
	protected Py4JServerConnection createConnection(Gateway gateway, Socket socket) throws IOException {
		InstrGatewayConnection connection = new InstrGatewayConnection(gateway, socket, getCustomCommands(), getListeners());
		connection.startConnection();
		return connection;
	}
}
