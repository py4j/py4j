package py4j.instrumented;

import py4j.CallbackClient;
import py4j.Py4JClientConnection;

import java.io.IOException;

public class InstrCallbackClient extends CallbackClient {

	public InstrCallbackClient(int port) {
		super(port);
		MetricRegistry.addCreatedObject(this);
	}

	@Override protected void finalize() throws Throwable {
		MetricRegistry.addFinalizedObject(this);
		super.finalize();
	}

	@Override
	protected Py4JClientConnection getConnection() throws IOException {
		Py4JClientConnection connection = null;

		connection = this.connections.pollLast();
		if (connection == null) {
			connection = new InstrCallbackConnection(port, address, socketFactory);
			connection.start();
		}

		return connection;
	}
}
