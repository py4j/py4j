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
		this(
				GatewayServer.DEFAULT_PORT, GatewayServer.defaultAddress(),
				GatewayServer.DEFAULT_PYTHON_PORT,
				GatewayServer.defaultAddress(),
				GatewayServer.DEFAULT_CONNECT_TIMEOUT,
				GatewayServer.DEFAULT_READ_TIMEOUT,
				ServerSocketFactory.getDefault(),
				SocketFactory.getDefault(), entryPoint);
	}

	public ClientServer(int javaPort, InetAddress javaAddress, int
			pythonPort, InetAddress pythonAddress, int connectTimeout, int
			readTimeout, ServerSocketFactory sSocketFactory, SocketFactory
			socketFactory, Object entryPoint) {
		this.javaPort = javaPort;
		this.javaAddress = javaAddress;
		this.pythonPort = pythonPort;
		this.pythonAddress = pythonAddress;
		this.connectTimeout = connectTimeout;
		this.readTimeout = readTimeout;
		this.sSocketFactory = sSocketFactory;
		this.socketFactory = socketFactory;

		this.pythonClient = new PythonClient(
				null, null, pythonPort, pythonAddress,
				CallbackClient.DEFAULT_MIN_CONNECTION_TIME, TimeUnit.SECONDS,
				SocketFactory.getDefault(), null);
		this.javaServer = new JavaServer(
				entryPoint, this.javaPort, this.connectTimeout,
				this.readTimeout, null, pythonClient);
		this.gateway = javaServer.getGateway();
		pythonClient.setGateway(gateway);
		pythonClient.setJavaServer(javaServer);
		// XXX Force gateway startup here
		this.gateway.startup();
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
