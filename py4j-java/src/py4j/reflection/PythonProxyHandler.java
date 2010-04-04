package py4j.reflection;

import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;
import java.util.logging.Logger;

import py4j.CommunicationChannelFactory;
import py4j.Gateway;
import py4j.Protocol;

public class PythonProxyHandler implements InvocationHandler {

	private final String id;

	private final CommunicationChannelFactory factory;

	private final Gateway gateway;

	private final Logger logger = Logger.getLogger(PythonProxyHandler.class
			.getName());

	public PythonProxyHandler(String id, CommunicationChannelFactory factory,
			Gateway gateway) {
		super();
		this.id = id;
		this.factory = factory;
		this.gateway = gateway;
	}

	@Override
	public Object invoke(Object proxy, Method method, Object[] args)
			throws Throwable {
		logger.info("Method " + method.getName() + " called on Python object "
				+ id);
		StringBuilder sBuilder = new StringBuilder();
		sBuilder.append(id);
		sBuilder.append("\n");
		sBuilder.append(method.getName());
		sBuilder.append("\n");

		if (args != null) {
			for (Object arg : args) {
				sBuilder.append(gateway.getReturnObject(arg).getCommandPart());
				sBuilder.append("\n");
			}
		}

		sBuilder.append("e\n");

		String returnCommand = factory.sendCommand(sBuilder.toString());

		return Protocol.getReturnValue(returnCommand, gateway);
	}

}
