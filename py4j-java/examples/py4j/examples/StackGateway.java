package py4j.examples;

import py4j.DefaultGateway;
import py4j.GatewayServer;

public class StackGateway extends DefaultGateway {

	public Stack createNewStack() {
		return new Stack();
	}
	
	public static void main(String[] args) {
		GatewayServer gateway = new GatewayServer(new StackGateway());
		gateway.start();
		System.out.println("Gateway Server Started");
	}
	
}
