package py4j;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.lang.reflect.Proxy;
import java.util.List;
import java.util.logging.Logger;

import py4j.reflection.PythonProxyHandler;

public class PythonProxyCommand extends AbstractCommand {
	private final Logger logger = Logger.getLogger(PythonProxyCommand.class
			.getName());

	public final static String PYTHON_PROXY_COMMAND_NAME = "p";

	public final static String PYTHON_PROXY_CREATE_SUB_COMMAND_NAME = "c";

	@Override
	public void execute(String commandName, BufferedReader reader,
			BufferedWriter writer) throws Py4JException, IOException {
		String returnCommand = null;
		String subCommand = reader.readLine();

		if (subCommand.equals(PYTHON_PROXY_CREATE_SUB_COMMAND_NAME)) {
			returnCommand = createProxy(reader);
		}
		logger.info("Returning command: " + returnCommand);
		writer.write(returnCommand);
		writer.flush();
	}

	private String createProxy(BufferedReader reader) throws IOException {
		String returnCommand = null;
		String objectId = reader.readLine();
		List<String> arguments = getStringArguments(reader);
		int size = arguments.size();

		try {
			Class<?>[] classes = new Class<?>[size];
			for (int i = 0; i < size; i++) {
				classes[i] = Class.forName(arguments.get(i));
			}

			Object proxy = Proxy.newProxyInstance(this.getClass()
					.getClassLoader(), classes, new PythonProxyHandler(
					objectId, null));
			gateway.putNewObject(proxy);
			returnCommand = Protocol.getOutputVoidCommand();
		} catch (Exception e) {
			// Problem while creating proxy
			returnCommand = Protocol.getOutputErrorCommand();
		}

		return returnCommand;
	}

}
