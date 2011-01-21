package py4j;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

import org.junit.Test;

public class GatewayServerTest {

	@Test
	public void testDoubleListen() {
		GatewayServer server1 = new GatewayServer(null);
		GatewayServer server2 = new GatewayServer(null);
		boolean valid = false;

		try {
			server1.start();
			server2.start();
			valid = false;
		} catch (Py4JNetworkException network) {
			valid = true;
		} catch (Exception e) {
			valid = false;
		}

		server1.shutdown();
		server2.shutdown();

		assertTrue(valid);
	}

	@Test
	public void testListener() {
		TestListener listener = new TestListener();
		GatewayServer server1 = new GatewayServer(null);
		server1.addListener(listener);
		server1.start();
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

class TestListener implements GatewayServerListener {

	public List<Long> values = new CopyOnWriteArrayList<Long>();

	@Override
	public void serverStarted() {
		values.add(new Long(1));
	}

	@Override
	public void serverStopped() {
		values.add(new Long(10));
	}

	@Override
	public void serverError(Exception e) {
		values.add(new Long(100));
	}

	@Override
	public void serverPreShutdown() {
		values.add(new Long(1000));
	}

	@Override
	public void serverPostShutdown() {
		values.add(new Long(10000));
	}

	@Override
	public void connectionStarted() {
		values.add(new Long(100000));
	}

	@Override
	public void connectionStopped() {
		values.add(new Long(1000000));
	}

	@Override
	public void connectionError(Exception e) {
		values.add(new Long(10000000));
	}

}