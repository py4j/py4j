package py4j;

import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.Reader;
import java.net.Socket;
import java.nio.charset.Charset;

public class EchoClient {

	private int port = EchoServer.SERVER_PORT;

	private Socket clientSocket;

	private Reader reader;

	private BufferedWriter writer;

	private char[] buffer = new char[4092];

	public int getPort() {
		return port;
	}

	public void setPort(int port) {
		this.port = port;
	}

	public void write(String command) throws IOException {
		writer.write(command);
		writer.flush();
	}

	public String getResponse() throws IOException {
		int count = reader.read(buffer);
		return new String(buffer, 0, count);
	}

	public void connect() throws IOException {
		clientSocket = new Socket("localhost", port);
		reader = new InputStreamReader(clientSocket.getInputStream(), Charset
				.forName("UTF-8"));
		writer = new BufferedWriter(new OutputStreamWriter(clientSocket
				.getOutputStream(), Charset.forName("UTF-8")));
	}

	public void close() {
		NetworkUtil.quietlyClose(reader);
		NetworkUtil.quietlyClose(writer);
		NetworkUtil.quietlyClose(clientSocket);
	}

}
