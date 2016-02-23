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
		// Wait for Python side to shut down Java side
		clientServer.startServer(false);

		// Shut down after 5 seconds
//		clientServer.startServer(true);
//		try {
//			Thread.currentThread().sleep(5000);
//		} catch (Exception e) {
//			e.printStackTrace();
//		}
//		clientServer.shutdown();

		System.out.println("Stopping");
	}
}
