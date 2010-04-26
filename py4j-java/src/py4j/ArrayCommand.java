package py4j;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.lang.reflect.Array;
import java.util.List;
import java.util.logging.Logger;

/**
 * <p>
 * A ArrayCommand is responsible for handling operations on arrays.
 * </p>
 * 
 * @author Barthelemy Dagenais
 * 
 */
public class ArrayCommand extends AbstractCommand {

	private final Logger logger = Logger
			.getLogger(ArrayCommand.class.getName());

	public static final String ARRAY_COMMAND_NAME = "a";

	public static final char ARRAY_GET_SUB_COMMAND_NAME = 'g';
	public static final char ARRAY_SET_SUB_COMMAND_NAME = 's';
	public static final char ARRAY_SLICE_SUB_COMMAND_NAME = 'l';
	public static final char ARRAY_LEN_SUB_COMMAND_NAME = 'e';
	public static final char ARRAY_CREATE_SUB_COMMAND_NAME = 'c';

	public static final String RETURN_VOID = Protocol.SUCCESS + ""
			+ Protocol.VOID + Protocol.END_OUTPUT;

	@Override
	public void execute(String commandName, BufferedReader reader,
			BufferedWriter writer) throws Py4JException, IOException {
		char subCommand = reader.readLine().charAt(0);
		String returnCommand = null;
		if (subCommand == ARRAY_GET_SUB_COMMAND_NAME) {
			returnCommand = getArray(reader);
		} else if (subCommand == ARRAY_SET_SUB_COMMAND_NAME) {
			returnCommand = setArray(reader);
		} else if (subCommand == ARRAY_SLICE_SUB_COMMAND_NAME) {
			returnCommand = sliceArray(reader);
		} else if (subCommand == ARRAY_LEN_SUB_COMMAND_NAME) {
			returnCommand = lenArray(reader);
		} else if (subCommand == ARRAY_CREATE_SUB_COMMAND_NAME) {
			returnCommand = createArray(reader);
		} else {
			returnCommand = Protocol.getOutputErrorCommand();
		}

		logger.info("Returning command: " + returnCommand);
		writer.write(returnCommand);
		writer.flush();

	}

	private String createArray(BufferedReader reader) throws IOException {
		String fqn = (String) Protocol.getObject(reader.readLine(), gateway);
		List<Object> dimensions = getArguments(reader);
		int size = dimensions.size();
		int[] dimensionsInt = new int[size];
		for (int i = 0; i < size; i++) {
			dimensionsInt[i] = (Integer) dimensions.get(i);
		}
		Object newArray = gateway.getReflectionEngine().createArray(fqn,
				dimensionsInt);
		ReturnObject returnObject = gateway.getReturnObject(newArray);
		return Protocol.getOutputCommand(returnObject);
	}

	private String setArray(BufferedReader reader) throws IOException {
		Object arrayObject = gateway.getObject(reader.readLine());
		int index = (Integer) Protocol.getObject(reader.readLine(), gateway);
		Object objectToSet = Protocol.getObject(reader.readLine(), gateway);

		// Read end
		reader.readLine();

		Array.set(arrayObject, index, objectToSet);
		return RETURN_VOID;
	}

	private String getArray(BufferedReader reader) throws IOException {
		Object arrayObject = gateway.getObject(reader.readLine());
		int index = (Integer) Protocol.getObject(reader.readLine(), gateway);
		// Read end
		reader.readLine();

		Object getObject = Array.get(arrayObject, index);
		ReturnObject returnObject = gateway.getReturnObject(getObject);
		return Protocol.getOutputCommand(returnObject);
	}

	private String lenArray(BufferedReader reader) throws IOException {
		Object arrayObject = gateway.getObject(reader.readLine());

		// Read end
		reader.readLine();

		int length = Array.getLength(arrayObject);
		ReturnObject returnObject = gateway.getReturnObject(length);
		return Protocol.getOutputCommand(returnObject);
	}

	private String sliceArray(BufferedReader reader) throws IOException {
		Object arrayObject = gateway.getObject(reader.readLine());
		List<Object> indices = getArguments(reader);
		int size = indices.size();
		Object newArray = gateway.getReflectionEngine().createArray(
				arrayObject.getClass().getComponentType().getName(),
				new int[] { size });
		for (int i = 0; i < size; i++) {
			int index = (Integer) indices.get(i);
			Array.set(newArray, i, Array.get(arrayObject, index));
		}
		ReturnObject returnObject = gateway.getReturnObject(newArray);
		return Protocol.getOutputCommand(returnObject);
	}
}
