package py4j;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.util.logging.Logger;

import py4j.model.HelpPageGenerator;
import py4j.model.Py4JClass;

public class HelpPageCommand extends AbstractCommand {
	private final Logger logger = Logger.getLogger(HelpPageCommand.class
			.getName());

	public final static String HELP_COMMAND_NAME = "h";

	public final static String HELP_OBJECT_SUB_COMMAND_NAME = "o";

	public final static String HELP_CLASS_SUB_COMMAND_NAME = "c";

	@Override
	public void execute(String commandName, BufferedReader reader,
			BufferedWriter writer) throws Py4JException, IOException {
		String returnCommand = null;
		String subCommand = reader.readLine();

		if (subCommand.equals(HELP_OBJECT_SUB_COMMAND_NAME)) {
			returnCommand = getHelpObject(reader);
		} else {
			returnCommand = getHelpClass(reader);
		}
		logger.info("Returning command: " + returnCommand);
		writer.write(returnCommand);
		writer.flush();
	}

	private String getHelpClass(BufferedReader reader) throws IOException {
		String className = reader.readLine();
		String shortName = reader.readLine();
		// EoC
		reader.readLine();
		String returnCommand = Protocol.getOutputErrorCommand();

		try {
			Py4JClass clazz = Py4JClass.buildClass(Class.forName(className));
			boolean isShortName = Protocol.getBoolean(shortName);
			String helpPage = HelpPageGenerator.getHelpPage(clazz, isShortName);
			ReturnObject rObject = gateway.getReturnObject(helpPage);
			returnCommand = Protocol.getOutputCommand(rObject);
		} catch (Exception e) {

		}

		return returnCommand;
	}

	private String getHelpObject(BufferedReader reader) throws IOException {
		String objectId = reader.readLine();
		String shortName = reader.readLine();
		// EoC
		reader.readLine();
		String returnCommand = Protocol.getOutputErrorCommand();

		try {
			Object obj = gateway.getObject(objectId);
			Py4JClass clazz = Py4JClass.buildClass(obj.getClass());
			boolean isShortName = Protocol.getBoolean(shortName);
			String helpPage = HelpPageGenerator.getHelpPage(clazz, isShortName);
			ReturnObject rObject = gateway.getReturnObject(helpPage);
			returnCommand = Protocol.getOutputCommand(rObject);
		} catch (Exception e) {

		}

		return returnCommand;
	}

}
