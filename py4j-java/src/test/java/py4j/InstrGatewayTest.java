package py4j;

import org.junit.Test;
import py4j.instrumented.InstrGatewayServer;
import py4j.instrumented.MetricRegistry;

import static org.junit.Assert.assertEquals;

public class InstrGatewayTest {

	private void startServer() {
		InstrGatewayServer server = new InstrGatewayServer(null, GatewayServer.DEFAULT_PORT, GatewayServer.DEFAULT_PYTHON_PORT);
		server.start();
		server.shutdown();
	}

	@Test
	public void testLifecycle() {
		startServer();
		System.gc();
		try {
			Thread.currentThread().sleep(1000);
		} catch(Exception e) {

		}
		assertEquals(2, MetricRegistry.getCreatedObjectsKeySet().size());
		assertEquals(2, MetricRegistry.getFinalizedObjectsKeySet().size());
		assertEquals(MetricRegistry.getCreatedObjectsKeySet(), MetricRegistry.getFinalizedObjectsKeySet());
	}
}
