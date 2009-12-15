package py4j.examples;

import py4j.DefaultGateway;
import py4j.GatewayServer;

public class BufferGateway extends DefaultGateway {

	private static GatewayServer server;
	
	public StringBuffer getStringBuffer() {
		StringBuffer sb = new StringBuffer("FromJava");
		return sb;
	}
	
	public static void main(String[] args) {
		server = new GatewayServer(new BufferGateway());
		server.start();
	}
	
	public static void stopGateway() {
		server.stop();
	}
	
}
