package py4j;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.fail;

import java.io.BufferedWriter;
import java.io.OutputStreamWriter;
import java.net.Socket;

import org.junit.Test;

public class EchoClientTest {
	
	@Test
	public void testConnection() {
		try {
			EchoServer.main(null);
			Socket testSocket = new Socket("localhost",EchoServer.TEST_PORT);
			BufferedWriter testWriter = new BufferedWriter(new OutputStreamWriter(testSocket.getOutputStream()));
			testWriter.write("yi7\n");
			testWriter.flush();
			testWriter.write("x\n");
			testWriter.flush();
			testWriter.close();
			testSocket.close();

			EchoClient client = new EchoClient();
			client.connect();
			client.write("c\ng\ngetExample\ne\n");
			assertEquals(client.getResponse(), "yi7");
			client.write("c\no1\nmethod1\ni1\nbtrue\ne\n");
			assertEquals(client.getResponse(), "x");
			client.close();
		} catch(Exception e) {
			e.printStackTrace();
			fail();
		} finally {
			
		}
	}
}
