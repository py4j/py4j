package py4j.reflection;

import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;
import java.util.logging.Logger;

import py4j.CommunicationChannelFactory;
import py4j.Gateway;
import py4j.Protocol;

/**
 * <p>
 * A PythonProxyHandler is used in place of a Python object. Python programs can
 * send Python objects that implements a Java interface to the JVM: these Python
 * objects are represented by dynamic proxies with a PythonProxyHandler.
 * </p>
 * 
 * @author Barthelemy Dagenais
 * 
 */
public class PythonProxyHandler implements InvocationHandler {

	private final String id;

	private final CommunicationChannelFactory factory;

	private final Gateway gateway;

	private final Logger logger = Logger.getLogger(PythonProxyHandler.class
			.getName());

	private final String finalizeCommand;

	public final static String CALL_PROXY_COMMAND_NAME = "c\n";

	public final static String GARBAGE_COLLECT_PROXY_COMMAND_NAME = "g\n";

	public PythonProxyHandler(String id, CommunicationChannelFactory factory,
			Gateway gateway) {
		super();
		this.id = id;
		this.factory = factory;
		this.gateway = gateway;
		this.finalizeCommand = GARBAGE_COLLECT_PROXY_COMMAND_NAME + id
				+ "\ne\n";
	}

	@Override
	public Object invoke(Object proxy, Method method, Object[] args)
			throws Throwable {
		logger.info("Method " + method.getName() + " called on Python object "
				+ id);
		StringBuilder sBuilder = new StringBuilder();
		sBuilder.append(CALL_PROXY_COMMAND_NAME);
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

	@Override
	protected void finalize() throws Throwable {
		try {
			logger.info("Finalizing python proxy id " + this.id);
			factory.sendCommand(finalizeCommand);
		} catch (Exception e) {
			logger
					.warning("Python Proxy ID could not send a finalize message: "
							+ this.id);
		} finally {
			super.finalize();
		}
	}

}
