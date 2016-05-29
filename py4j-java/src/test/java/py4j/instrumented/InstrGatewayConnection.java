package py4j.instrumented;

import py4j.Gateway;
import py4j.GatewayConnection;
import py4j.GatewayServerListener;
import py4j.commands.Command;

import java.io.IOException;
import java.net.Socket;
import java.util.List;

public class InstrGatewayConnection extends GatewayConnection {
	public InstrGatewayConnection(Gateway gateway, Socket socket, List<Class<? extends Command>> customCommands,
			List<GatewayServerListener> listeners) throws IOException {
		super(gateway, socket, customCommands, listeners);
		MetricRegistry.addCreatedObject(this);
	}

	@Override protected void finalize() throws Throwable {
		MetricRegistry.addFinalizedObject(this);
		super.finalize();
	}
}
