package py4j.instrumented;

import py4j.CallbackConnection;

import javax.net.SocketFactory;
import java.net.InetAddress;

public class InstrCallbackConnection extends CallbackConnection {

	public InstrCallbackConnection(int port, InetAddress address, SocketFactory socketFactory) {
		super(port, address, socketFactory);
		MetricRegistry.addCreatedObject(this);
	}

	@Override protected void finalize() throws Throwable {
		MetricRegistry.addFinalizedObject(this);
		super.finalize();
	}

}
