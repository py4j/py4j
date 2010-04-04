package py4j;

import static org.junit.Assert.assertEquals;

import java.io.BufferedReader;
import java.io.BufferedWriter;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

public class ProxyTest {

	private GatewayServer gServer;
	private PythonClient pClient;

	@Before
	public void setup() {
		GatewayServer.turnLoggingOn();
		gServer = new GatewayServer(new InterfaceEntry());
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
		String message = "c\nt\nsayHello\npp123;py4j.IHello\ne\n";
		pClient.nextProxyReturnMessage = "ysHello World";
		pClient.sendMesage(message);
		assertEquals("p123\nhello\ne\n", pClient.lastProxyMessage);
		assertEquals("ysHello World", pClient.lastReturnMessage);
		
		// TODO
		// 1- Convert String with \n (currently not converted!!!)
		// 2- Test with errors
		// 3- Test with parameters (e.g., hello(String, int, Object already in gateway)
	}

}

interface IHello {

	public String hello();

}

class InterfaceEntry {

	public String sayHello(IHello obj) {
		return obj.hello();
	}

}
