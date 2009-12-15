package py4j;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.fail;

import org.junit.Test;

import py4j.examples.BufferGateway;

public class BufferGatewayTest {

	@Test
	public void testBufferedGateway1() {
		BufferGateway.main(null);
		EchoClient client = new EchoClient();

		try {
			client.connect();
			client.write("c\ng\ngetStringBuffer\ne\n");
			assertEquals(client.getResponse(),"yro0");
			client.write("c\no0\nappend\nd1.1\ne\n");
			assertEquals(client.getResponse(),"yro1");
			client.write("c\no0\ntoString\ne\n");
			assertEquals(client.getResponse(),"ysFromJava1.1");
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		} finally {
			client.close();
			BufferGateway.stopGateway();
		}
	}

}
