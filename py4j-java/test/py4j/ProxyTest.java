package py4j;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.assertFalse;

import java.util.ArrayList;
import java.util.List;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

public class ProxyTest {

	private GatewayServer gServer;
	private PythonClient pClient;
	private InterfaceEntry entry;

	@Before
	public void setup() {
		GatewayServer.turnLoggingOn();
		entry = new InterfaceEntry();
		gServer = new GatewayServer(entry);
		pClient = new PythonClient();
		gServer.start();
		pClient.startProxy();
		try {
			Thread.sleep(250);
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	@After
	public void teardown() {
		gServer.shutdown();
		pClient.stopProxy();
		try {
			Thread.sleep(250);
		} catch (Exception e) {
			e.printStackTrace();
		}
		GatewayServer.turnLoggingOff();
	}
	
	@Test
	public void testSayHello() {
		String message = "c\nt\nsayHello\nfp123;py4j.IHello\ne\n";
		pClient.nextProxyReturnMessage = "ysHello\\nWorld";
		pClient.sendMesage(message);
		assertEquals("c\np123\nhello\ne\n", pClient.lastProxyMessage);
		assertEquals("ysHello\\nWorld", pClient.lastReturnMessage);
		assertEquals("Hello\nWorld",entry.simpleHello);
	}
	
	@Test
	public void testSayHelloWithParams() {
		String message = "c\nt\nsayHelloParams\nfp123;py4j.IHello\ne\n";
		pClient.nextProxyReturnMessage = "ysHello\\nWorld";
		pClient.sendMesage(message);
		assertEquals("c\np123\nhello2\nsTesting\\nWild\ni3\nlo0\ne\n", pClient.lastProxyMessage);
		assertEquals("ysHello\\nWorld", pClient.lastReturnMessage);
		assertEquals("Hello\nWorld",entry.simpleHello2);
	}
	
	@Test
	public void testSayHelloError() {
		assertFalse(entry.exception);
		String message = "c\nt\nsayHelloError\nfp123;py4j.IHello\ne\n";
		pClient.nextProxyReturnMessage = "x";
		pClient.sendMesage(message);
		assertEquals("c\np123\nhello\ne\n", pClient.lastProxyMessage);
		assertTrue(entry.exception);
		assertEquals("yv", pClient.lastReturnMessage);
		
	}

}


interface IHello {

	public String hello();

	@SuppressWarnings("unchecked")
	public String hello2(String param1, int param2, List param3);
	
}


class InterfaceEntry {
	
	public String simpleHello;
	public String simpleHello2;
	public boolean exception = false;
	public String sayHello(IHello obj) {
		simpleHello = obj.hello();
		return simpleHello;
	}
	
	public String sayHelloParams(IHello obj) {
		simpleHello2 = obj.hello2("Testing\nWild", 3, new ArrayList<String>());
		return simpleHello2;
	}
	
	public void sayHelloError(IHello obj) {
		try {
			obj.hello();
		} catch(Py4JException e) {
			exception = true;
		}
	}

}
