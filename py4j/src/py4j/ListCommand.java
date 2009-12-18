package py4j;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.util.ArrayList;
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

	public static final char LIST_CONCAT_COMMAND = 'a';
	public static final char LIST_MULT_COMMAND = 'm';
	public static final char LIST_IMULT_COMMAND = 'i';
	public static final char LIST_COUNT_COMMAND = 'f';

	public static final String RETURN_VOID = Protocol.SUCCESS + ""
			+ Protocol.VOID;

	@Override
	public void execute(String command, BufferedReader reader,
			BufferedWriter writer) throws Py4JException, IOException {
		char listCommand = reader.readLine().charAt(0);
		String returnCommand = null;
		if (listCommand == LIST_SLICE_COMMAND) {
			// TODO!
		} else if (listCommand == LIST_CONCAT_COMMAND) {
			returnCommand = concat_list(reader);
		} else if (listCommand == LIST_MULT_COMMAND) {
			returnCommand = mult_list(reader);
		} else if (listCommand == LIST_IMULT_COMMAND) {
			returnCommand = imult_list(reader);
		} else if (listCommand == LIST_COUNT_COMMAND) {
			returnCommand = count_list(reader);
		} else {
			returnCommand = call_collections_method(reader, listCommand);
		}

		logger.info("Returning command: " + returnCommand);
		writer.write(returnCommand);
		writer.flush();
	}

	@SuppressWarnings("unchecked")
	private String count_list(BufferedReader reader) throws IOException {
		List list1 = (List) gateway.getObject(reader.readLine());
		Object objectToCount = Protocol.getObject(reader.readLine(), gateway);
		
		// Read end
		reader.readLine();
		
		int count = Collections.frequency(list1, objectToCount);
		ReturnObject returnObject = gateway.getReturnObject(count);
		return Protocol.getOutputCommand(returnObject);
	}

	@SuppressWarnings("unchecked")
	private String imult_list(BufferedReader reader) throws IOException {
		List list1 = (List) gateway.getObject(reader.readLine());
		List tempList = new ArrayList(list1.subList(0, list1.size()));
		int n = Protocol.getInteger(reader.readLine());
		// Read end
		reader.readLine();

		if (n <= 0) {
			list1.clear();
		} else {
			for (int i = 1; i < n; i++) {
				list1.addAll(tempList);
			}
		}

		return RETURN_VOID;
	}

	@SuppressWarnings("unchecked")
	private String mult_list(BufferedReader reader) throws IOException {
		List list1 = (List) gateway.getObject(reader.readLine());
		int n = Protocol.getInteger(reader.readLine());
		// Read end
		reader.readLine();

		List list2 = new ArrayList();
		for (int i = 0; i < n; i++) {
			list2.addAll(list1);
		}
		ReturnObject returnObject = gateway.getReturnObject(list2);
		return Protocol.getOutputCommand(returnObject);
	}

	@SuppressWarnings("unchecked")
	private String concat_list(BufferedReader reader) throws IOException {
		List list1 = (List) gateway.getObject(reader.readLine());
		List list2 = (List) gateway.getObject(reader.readLine());
		// Read end
		reader.readLine();

		List list3 = new ArrayList(list1);
		list3.addAll(list2);
		ReturnObject returnObject = gateway.getReturnObject(list3);
		return Protocol.getOutputCommand(returnObject);
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
