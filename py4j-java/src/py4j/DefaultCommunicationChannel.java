package py4j;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.InetAddress;
import java.net.Socket;
import java.nio.charset.Charset;

public class DefaultCommunicationChannel implements CommunicationChannel {

	private boolean used;

	private final int port;

	private final InetAddress address;

	private Socket socket;

	private BufferedReader reader;

	private BufferedWriter writer;

	public DefaultCommunicationChannel(int port, InetAddress address) {
		super();
		this.port = port;
		this.address = address;
	}

	@Override
	public void start() throws IOException {
		socket = new Socket(address, port);
		reader = new BufferedReader(new InputStreamReader(socket
				.getInputStream(), Charset.forName("UTF-8")));
		writer = new BufferedWriter(new OutputStreamWriter(socket
				.getOutputStream(), Charset.forName("UTF-8")));
	}

	@Override
	public String sendCommand(String command) {
		String returnCommand = null;
		try {
			writer.write(command);
			writer.flush();
			returnCommand = reader.readLine();
		} catch (Exception e) {
			throw new Py4JNetworkException("Error while sending a command: "
					+ command, e);
		}
		return returnCommand;
	}

	@Override
	public void setUsed(boolean used) {
		this.used = used;
	}

	@Override
	public void shutdown() {
		NetworkUtil.quietlyClose(reader);
		NetworkUtil.quietlyClose(writer);
		NetworkUtil.quietlyClose(socket);
	}

	@Override
	public boolean wasUsed() {
		return used;
	}

}
