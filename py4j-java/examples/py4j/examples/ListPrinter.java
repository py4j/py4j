package py4j.examples;

import java.util.List;

import py4j.GatewayServer;

public class ListPrinter {

	public String getListAsString(List<?> list) {
		StringBuffer sb = new StringBuffer();
		for (Object o: list) {
			sb.append(o.toString());
		}
		return sb.toString();
	}
	
	public static void main(String[] args) {
		GatewayServer server = new GatewayServer(new ListPrinter());
		server.start();
	}
	
}
