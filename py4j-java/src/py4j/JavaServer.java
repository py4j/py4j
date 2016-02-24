package py4j;

import py4j.commands.Command;

import java.io.IOException;
import java.net.Socket;
import java.util.List;

/**
 * Created by barthelemy on 2016-02-12.
 */
public class JavaServer extends GatewayServer {

	public JavaServer(Object entryPoint, int port, int connectTimeout,
			int readTimeout, List<Class<? extends Command>> customCommands,
			Py4JPythonClient pythonClient) {
		super(entryPoint, port, connectTimeout, readTimeout, customCommands,
				pythonClient);
	}

	@Override
	protected Py4JServerConnection createConnection(Gateway gateway, Socket socket)
			throws IOException {
		ClientServerConnection connection = new ClientServerConnection(gateway,
				socket, getCustomCommands(), getCallbackClient(), this);
		connection.startServerConnection();
		return connection;
	}
}
