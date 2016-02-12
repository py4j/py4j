package py4j;

import py4j.commands.Command;

import javax.net.ServerSocketFactory;
import javax.net.SocketFactory;
import java.io.*;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.charset.Charset;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Created by barthelemy on 2016-02-09.
 */
public class ClientServer {

	private final int javaPort;

	private final InetAddress javaAddress;

	private final int pythonPort;

	private final InetAddress pythonAddress;

	private int listeningPort;

	private final int connectTimeout;

	private final int readTimeout;

	private final ServerSocketFactory sSocketFactory;

	private final SocketFactory socketFactory;

	private final Gateway gateway;

	private final JavaServer javaServer;

	private final PythonClient pythonClient;

	protected final Logger logger = Logger.getLogger(ClientServer.class
			.getName());


	public ClientServer(Object entryPoint) {
		// TODO NOT SURE WE NEED TO KEEP THESE PROPERTIES HERE
		this.javaPort = GatewayServer.DEFAULT_PORT;
		this.javaAddress = GatewayServer.defaultAddress();
		this.pythonPort = GatewayServer.DEFAULT_PYTHON_PORT;
		this.pythonAddress = GatewayServer.defaultAddress();
		this.connectTimeout = GatewayServer.DEFAULT_CONNECT_TIMEOUT;
		this.readTimeout = GatewayServer.DEFAULT_READ_TIMEOUT;
		this.sSocketFactory = ServerSocketFactory.getDefault();
		this.socketFactory = SocketFactory.getDefault();
		this.pythonClient = new PythonClient(
				null, null, null, pythonPort, pythonAddress,
				CallbackClient.DEFAULT_MIN_CONNECTION_TIME, TimeUnit.SECONDS,
				SocketFactory.getDefault());
		this.javaServer = new JavaServer(
				entryPoint, this.javaPort, this.connectTimeout,
				this.readTimeout, null, pythonClient);
		this.gateway = javaServer.getGateway();
		pythonClient.setGateway(gateway);
		// TODO Not very reliable because listeners added to GatewayServer
		// won't be added here.
		pythonClient.setListeners(javaServer.getListeners());
	}

	public Py4JJavaServer getJavaServer() {
		return javaServer;
	}

	public Py4JPythonClient getPythonClient() {
		return pythonClient;
	}

	public void startServer(boolean fork) {
		javaServer.start(fork);
	}

	public void shutdown() {
		this.javaServer.shutdown(true);
	}

	public Object getPythonServerEntryPoint(Class[] interfacesToImplement) {
		Object proxy = Protocol.getPythonProxyHandler(gateway.getClass()
				.getClassLoader(), interfacesToImplement, Protocol.ENTRY_POINT_OBJECT_ID,
				gateway);
		return proxy;
	}

}
