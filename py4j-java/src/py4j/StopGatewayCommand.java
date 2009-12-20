package py4j;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;

public class StopGatewayCommand extends AbstractCommand {

	private final GatewayServer gatewayServer;
	
	public StopGatewayCommand(GatewayServer gatewayServer) {
		this.gatewayServer = gatewayServer;
	}
	
	@Override
	public void execute(String command, BufferedReader reader,
			BufferedWriter writer) throws Py4JException, IOException {
		this.gatewayServer.stop();
	}

}
