package py4j.reflection;

import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;
import java.util.logging.Logger;

import py4j.CommunicationChannelFactory;

public class PythonProxyHandler implements InvocationHandler {

	private final String id;

	private final CommunicationChannelFactory factory;

	private final Logger logger = Logger.getLogger(PythonProxyHandler.class
			.getName());

	public PythonProxyHandler(String id, CommunicationChannelFactory factory) {
		super();
		this.id = id;
		this.factory = factory;
	}

	@Override
	public Object invoke(Object proxy, Method method, Object[] args)
			throws Throwable {
		logger.info("Method " + method.getName() + " called on Python object "
				+ id);

		return null;
	}

}
