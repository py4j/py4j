package py4j;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.logging.Logger;

public class ListCommand extends AbstractCommand {

	private final Logger logger = Logger.getLogger(ListCommand.class.getName());

	public static final char LIST_SORT_COMMAND = 's';
	public static final char LIST_REVERSE_COMMAND = 'r';
	public static final char LIST_MAX_COMMAND = 'x';
	public static final char LIST_MIN_COMMAND = 'n';
	public static final char LIST_SLICE_COMMAND = 'l';

	public static final String RETURN_VOID = Protocol.SUCCESS + ""
			+ Protocol.VOID;

	@Override
	public void execute(String command, BufferedReader reader,
			BufferedWriter writer) throws Py4JException, IOException {
		char listCommand = reader.readLine().charAt(0);
		String returnCommand = null;
		if (listCommand == LIST_SLICE_COMMAND) {
			// TODO!
		} else {
			returnCommand = call_collections_method(reader, listCommand);
		}

		logger.info("Returning command: " + returnCommand);
		writer.write(returnCommand);
		writer.flush();
	}

	@SuppressWarnings("unchecked")
	private String call_collections_method(BufferedReader reader,
			char listCommand) throws IOException {
		String returnCommand;
		String list_id = reader.readLine();
		
		// Read end of command
		reader.readLine();
		
		List list = (List) gateway.getObject(list_id);
		try {
			if (listCommand == LIST_SORT_COMMAND) {
				returnCommand = sort_list(list);
			} else if (listCommand == LIST_REVERSE_COMMAND) {
				returnCommand = reverse_list(list);
			} else if (listCommand == LIST_MAX_COMMAND) {
				returnCommand = max_list(list);
			} else if (listCommand == LIST_MIN_COMMAND) {
				returnCommand = min_list(list);
			} else {
				returnCommand = Protocol.getOutputErrorCommand();
			}
		} catch (Exception e) {
			returnCommand = Protocol.getOutputErrorCommand();
		}
		return returnCommand;
	}

	@SuppressWarnings("unchecked")
	private String min_list(List list) {
		Object object = Collections.min(list);
		ReturnObject returnObject = gateway.getReturnObject(object);
		return Protocol.getOutputCommand(returnObject);
	}

	@SuppressWarnings("unchecked")
	private String max_list(List list) {
		Object object = Collections.max(list);
		ReturnObject returnObject = gateway.getReturnObject(object);
		return Protocol.getOutputCommand(returnObject);
	}

	@SuppressWarnings("unchecked")
	private String reverse_list(List list) {
		Collections.reverse(list);
		return RETURN_VOID;
	}

	@SuppressWarnings("unchecked")
	private String sort_list(List list) {
		Collections.sort(list);
		return RETURN_VOID;
	}

}
