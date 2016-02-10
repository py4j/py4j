package py4j.examples;

import py4j.ClientServer;
import py4j.GatewayServer;

import java.util.logging.ConsoleHandler;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Created by barthelemy on 2016-02-10.
 */
public class SingleThreadApplication {

	public static void main(String[] args) {
		GatewayServer.turnAllLoggingOn();
		Logger logger = Logger.getLogger("py4j");
		logger.setLevel(Level.ALL);
		ConsoleHandler handler = new ConsoleHandler();
		handler.setLevel(Level.FINEST);
		logger.addHandler(handler);
		System.out.println("Starting");
		ExampleEntryPoint point = new ExampleEntryPoint();
		ClientServer clientServer = new ClientServer(point);
		clientServer.start();
		System.out.println("Stopping");
	}
}
