package py4j;

import org.junit.Test;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

public class ClientServerTest {

	@Test
	public void testListenerClientServer() {
		TestListener listener = new TestListener();
		ClientServer server1 = new ClientServer(null);
		Py4JJavaServer javaServer = server1.getJavaServer();
		javaServer.addListener(listener);
		server1.startServer(true);
		try {
			Thread.sleep(250);
		} catch (Exception e) {

		}
		server1.shutdown();
		try {
			Thread.sleep(250);
		} catch (Exception e) {

		}
		// Started, PreShutdown, Error, Stopped, PostShutdown
		// But order cannot be guaranteed because two threads are competing.
		assertTrue(listener.values.contains(new Long(1)));
		assertTrue(listener.values.contains(new Long(10)));
		assertTrue(listener.values.contains(new Long(100)));
		assertTrue(listener.values.contains(new Long(1000)));
		assertTrue(listener.values.contains(new Long(10000)));
		assertEquals(5, listener.values.size());
	}
}
