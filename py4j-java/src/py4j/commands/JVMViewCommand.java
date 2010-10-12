package py4j.commands;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.util.logging.Logger;

import py4j.Gateway;
import py4j.Py4JException;
import py4j.reflection.ReflectionEngine;

public class JVMViewCommand extends AbstractCommand {

	private final Logger logger = Logger.getLogger(JVMViewCommand.class
			.getName());

	public final static char CREATE_VIEW_SUB_COMMAND_NAME = 'c';

	public final static char IMPORT_SUB_COMMAND_NAME = 'i';

	public final static char SEARCH_SUB_COMMAND_NAME = 's';
	
	public static final String JVMVIEW_COMMAND_NAME = "j";

	protected ReflectionEngine rEngine;

	public JVMViewCommand() {
		super();
		this.commandName = JVMVIEW_COMMAND_NAME;
	}

	@Override
	public void init(Gateway gateway) {
		super.init(gateway);
		rEngine = gateway.getReflectionEngine();
	}

	@Override
	public void execute(String commandName, BufferedReader reader,
			BufferedWriter writer) throws Py4JException, IOException {
		char subCommand = reader.readLine().charAt(0);
		String returnCommand = null;

		if (subCommand == CREATE_VIEW_SUB_COMMAND_NAME) {
			returnCommand = createJVMView(reader);
		} else if (subCommand == IMPORT_SUB_COMMAND_NAME){
			returnCommand = doImport(reader);
		} else {
			returnCommand = search(reader);
		}
		logger.info("Returning command: " + returnCommand);
		writer.write(returnCommand);
		writer.flush();
	}

	private String search(BufferedReader reader) {
		return null;
	}

	private String doImport(BufferedReader reader) {
		return null;
	}

	private String createJVMView(BufferedReader reader) {
		return null;
	}

}
