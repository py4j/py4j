package py4j.examples;

import py4j.GatewayServer;

public class StackEntryPoint {

	public Stack createNewStack() {
		return new Stack();
	}
	
	public static void main(String[] args) {
		GatewayServer gateway = new GatewayServer(new StackEntryPoint());
		gateway.start();
		System.out.println("Gateway Server Started");
	}
	
}
