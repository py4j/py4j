package py4j;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.util.logging.Logger;

public class MemoryCommand extends AbstractCommand {

	private final Logger logger = Logger
			.getLogger(MemoryCommand.class.getName());

	public final static String MEMORY_COMMAND_NAME = "m";

	public final static String MEMORY_DEL_COMMAND_NAME = "d";

	public final static String MEMORY_ATTACH_SUB_COMMAND_NAME = "a";

	@Override
	public void execute(String commandName, BufferedReader reader,
			BufferedWriter writer) throws Py4JException, IOException {
		String returnCommand = null;
		String subCommand = reader.readLine();

		if (subCommand.equals(MEMORY_DEL_COMMAND_NAME)) {
			returnCommand = deleteObject(reader);
		} else {
			returnCommand = attachObject(reader);
		}
		logger.info("Returning command: " + returnCommand);
		writer.write(returnCommand);
		writer.flush();
	}

	private String attachObject(BufferedReader reader) throws IOException {
		String objectId = reader.readLine();
		// EoC
		reader.readLine();
		String returnCommand = Protocol.getOutputErrorCommand();
		try {
			ReturnObject rObject = gateway.attachObject(objectId);
			returnCommand = Protocol.getOutputCommand(rObject);
		} catch(Exception e) {
			
		}
		
		return returnCommand;
	}

	private String deleteObject(BufferedReader reader) throws IOException {
		String objectId = reader.readLine();
		// EoC
		reader.readLine();
		
		gateway.deleteObject(objectId);
		
		return Protocol.getOutputVoidCommand();
	}

}
