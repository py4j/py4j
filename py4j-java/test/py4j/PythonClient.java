package py4j;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;

public class PythonClient implements Runnable {

	public volatile String lastProxyMessage;
	public volatile String lastReturnMessage;
	public volatile String nextProxyReturnMessage;
	
	private ServerSocket sSocket;
	
	public void startProxy() {
		new Thread(this).start();
	}
	
	public void run() {
		try {
			sSocket = new ServerSocket(25334);
			Socket socket = sSocket.accept();
			BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
			BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream()));
			lastProxyMessage = "";
			String temp = reader.readLine() + "\n";
			lastProxyMessage += temp;
			while (!temp.equals("e\n")) {
				temp = reader.readLine() + "\n";
				lastProxyMessage += temp;
			}
			writer.write(nextProxyReturnMessage);
			writer.flush();
			writer.close();
			reader.close();
			socket.close();
		} catch(Exception e) {
			e.printStackTrace();
		}
	}
	
	public void stopProxy() {
		NetworkUtil.quietlyClose(sSocket);
	}
	
	public void sendMesage(String message) {
		try {
			Socket socket = new Socket(InetAddress.getLocalHost(), 25333);
			BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
			BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream()));
			writer.write(message);
			writer.flush();
			lastReturnMessage = reader.readLine();
			writer.close();
			reader.close();
			socket.close();
		} catch(Exception e) {
			e.printStackTrace();
		}
	}
	
}
