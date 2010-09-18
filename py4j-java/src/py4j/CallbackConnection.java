package py4j;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.InetAddress;
import java.net.Socket;
import java.nio.charset.Charset;
import java.util.logging.Logger;

/**
 * <p>
 * Default implementation of the CommunicationChannel interface using TCP
 * sockets.
 * </p>
 * 
 * @author Barthelemy Dagenais
 * 
 */
public class CallbackConnection {

	private boolean used;

	private final int port;

	private final InetAddress address;

	private Socket socket;

	private BufferedReader reader;

	private BufferedWriter writer;

	private final Logger logger = Logger
			.getLogger(CallbackConnection.class.getName());

	public CallbackConnection(int port, InetAddress address) {
		super();
		this.port = port;
		this.address = address;
	}

	public void start() throws IOException {
		logger.info("Starting Communication Channel on " + address + " at "
				+ port);
		socket = new Socket(address, port);
		reader = new BufferedReader(new InputStreamReader(socket
				.getInputStream(), Charset.forName("UTF-8")));
		writer = new BufferedWriter(new OutputStreamWriter(socket
				.getOutputStream(), Charset.forName("UTF-8")));
	}

	public String sendCommand(String command) {
		String returnCommand = null;
		try {
			this.used = true;
			writer.write(command);
			writer.flush();
			returnCommand = reader.readLine();
		} catch (Exception e) {
			throw new Py4JNetworkException("Error while sending a command: "
					+ command, e);
		}
		return returnCommand;
	}

	public void setUsed(boolean used) {
		this.used = used;
	}

	public void shutdown() {
		NetworkUtil.quietlyClose(reader);
		NetworkUtil.quietlyClose(writer);
		NetworkUtil.quietlyClose(socket);
	}

	public boolean wasUsed() {
		return used;
	}

}
