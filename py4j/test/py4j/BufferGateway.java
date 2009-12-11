package py4j;

public class BufferGateway extends DefaultGateway {

	public StringBuffer getStringBuffer() {
		StringBuffer sb = new StringBuffer("FromJava");
		return sb;
	}
	
	public static void main(String[] args) {
		GatewayServer server = new GatewayServer(new BufferGateway());
		server.start();
	}
	
}
