package py4j.examples;

import py4j.GatewayServer;

public class AdditionApplication {

	public int addition(int first, int second) {
		return first + second;
	}
	
	public static void main(String[] args) {
		AdditionApplication app = new AdditionApplication();
		GatewayServer server = new GatewayServer(app);
		server.start();
	}

}
