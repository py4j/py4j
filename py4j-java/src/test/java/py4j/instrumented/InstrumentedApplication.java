package py4j.instrumented;

import py4j.GatewayServer;

public class InstrumentedApplication {

	public void startServer2() {
		InstrGatewayServer server2 = new InstrGatewayServer(this, GatewayServer.DEFAULT_PORT + 5, GatewayServer
				.DEFAULT_PYTHON_PORT + 5);
		server2.start();
	}

	public static void main(String[] args) {
		InstrumentedApplication app = new InstrumentedApplication();
		GatewayServer server = new GatewayServer(app);
		server.start();
	}
}
