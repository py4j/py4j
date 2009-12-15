package py4j;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.charset.Charset;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

public class EchoServer {

	public static final int TEST_PORT = 25332;
	
	public static final int SERVER_PORT = 25333;
	
	private int testPort = TEST_PORT;

	private int serverPort = SERVER_PORT;

	private final BlockingQueue<String> queue = new LinkedBlockingQueue<String>();

	public int getTestPort() {
		return testPort;
	}

	public void setTestPort(int testPort) {
		this.testPort = testPort;
	}

	public int getServerPort() {
		return serverPort;
	}

	public void setServerPort(int serverPort) {
		this.serverPort = serverPort;
	}

	private void setupTestServer() {
		Thread t = new Thread(new Runnable() {

			@Override
			public void run() {
				ServerSocket sSocket = null;
				Socket testSocket = null;
				try {
					sSocket = new ServerSocket(testPort);
					testSocket = sSocket.accept();
					BufferedReader reader = new BufferedReader(
							new InputStreamReader(testSocket.getInputStream(), Charset.forName("UTF-8")));
					while (true) {
						System.out.println("Waiting for echo input.");
						String command = reader.readLine();
						System.out.println("Echo received: " + command);
						if (command == null) {
							break;
						}
						queue.put(command);
					}
				} catch (Exception e) {
					e.printStackTrace();
				} finally {
					NetworkUtil.quietlyClose(testSocket);
					NetworkUtil.quietlyClose(sSocket);
				}
			}

		});

		t.start();
	}
	
	private void setupServer() {
		Thread t = new Thread(new Runnable() {

			@Override
			public void run() {
				ServerSocket sSocket = null;
				Socket clientSocket = null;
				try {
					sSocket = new ServerSocket(serverPort);
					clientSocket = sSocket.accept();
					BufferedReader reader = new BufferedReader(
							new InputStreamReader(clientSocket.getInputStream(), Charset.forName("UTF-8")));
					BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(clientSocket.getOutputStream(), Charset.forName("UTF-8")));
					while (true) {
						String command = readCommand(reader);
						if (command == null) {
							break;
						}
						String returnCommand = queue.poll();
						System.out.println(returnCommand);
						writer.write(returnCommand);
						writer.flush();
					}
				} catch (Exception e) {
					e.printStackTrace();
				} finally {
					NetworkUtil.quietlyClose(clientSocket);
					NetworkUtil.quietlyClose(sSocket);
				}
			}

			private String readCommand(BufferedReader reader) throws IOException {
				System.out.println("Reading commands");
				StringBuilder commandBuilder = new StringBuilder();
				
				while (true) {
					String temp = reader.readLine();
					System.out.println("Received temp: " + temp);
					if (temp != null) {
						commandBuilder.append(temp);
						commandBuilder.append("\n");
						if (temp.trim().equals("e")) {
							break;
						}
					} else {
						break;
					}
				}
				
				String command = commandBuilder.toString().trim();
				if (command.length() == 0) {
					command = null;
				}
				
				return command;
			}

		});

		t.start();		
	}
	
	public static void main(String[] args) {
		EchoServer echoServer = new EchoServer();
		echoServer.setupTestServer();
		echoServer.setupServer();
	}

	
}
