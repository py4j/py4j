package py4j;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.util.List;
import java.util.logging.Logger;

public class ListCommand extends AbstractCommand {
	
	private final Logger logger = Logger.getLogger(ListCommand.class.getName());

	@Override
	public void execute(String command, BufferedReader reader,
			BufferedWriter writer) throws Py4JException, IOException {
		String targetObjectId = reader.readLine();
		String methodName = reader.readLine();
		List<Argument> arguments = getArguments(reader);

		ReturnObject returnObject = getReturnObject(methodName, targetObjectId, arguments);
		
		String returnCommand = Protocol.getOutputCommand(returnObject);
		logger.info("Returning command: " + returnCommand);
		writer.write(returnCommand);
		writer.flush();
	}

	
	
}
