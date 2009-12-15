package py4j;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.fail;

import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.Reader;
import java.net.Socket;

import org.junit.Test;

public class EchoServerTest {

	@Test
	public void testConnection() {
		try {
			EchoServer.main(null);
			Socket testSocket = new Socket("localhost", EchoServer.TEST_PORT);
			BufferedWriter testWriter = new BufferedWriter(
					new OutputStreamWriter(testSocket.getOutputStream()));
			// EchoServer requires end of line character to delimit commands.
			// Otherwise, it sometimes gets confused and can join two commands
			// together which is bad. I (bart) don't know why this happens.
			testWriter.write("yi7\n");
			testWriter.flush();
			testWriter.write("x\n");
			testWriter.flush();
			testWriter.close();
			testSocket.close();

			char[] buffer = new char[4092];
			Socket clientSocket = new Socket("localhost",
					EchoServer.SERVER_PORT);
			Reader clientReader = new InputStreamReader(clientSocket
					.getInputStream());
			BufferedWriter clientWriter = new BufferedWriter(
					new OutputStreamWriter(clientSocket.getOutputStream()));

			clientWriter.write("c\ng\ngetExample\ne\n");
			clientWriter.flush();
			int count = clientReader.read(buffer);
			assertEquals(new String(buffer, 0, count), "yi7");
			clientWriter.write("c\no1\nmethod1\ni1\nbtrue\ne\n");
			clientWriter.flush();
			count = clientReader.read(buffer);
			assertEquals(new String(buffer, 0, count), "x");

			clientReader.close();
			clientWriter.close();
			clientSocket.close();
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

}
