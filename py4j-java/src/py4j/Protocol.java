/*******************************************************************************
 * 
 * Copyright (c) 2009, 2010, Barthelemy Dagenais All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 * 
 * - Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
 * 
 * - Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 * 
 * - The name of the author may not be used to endorse or promote products
 * derived from this software without specific prior written permission.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 *******************************************************************************/
package py4j;

import java.lang.reflect.Proxy;

import py4j.reflection.PythonProxyHandler;

/**
 * <p>
 * This class defines the protocol used to communicate between two virtual
 * machines (e.g., Python and Java).
 * </p>
 * <p>
 * Currently, the protocol requires type information (e.g., is this string an
 * integer, an object reference or a boolean?) to be embedded with each command
 * part. The rational is that the source virtual machine is usually better at
 * determining the type of objects it sends.
 * </p>
 * <p>
 * An input command is usually composed of:
 * </p>
 * <ul>
 * <li>A command name (e.g., c for call)</li>
 * <li>Optionally, a sub command name (e.g., 'a' for concatenate in the list
 * command)</li>
 * <li>A list of command parts (e.g., the name of a method, the value of a
 * parameter, etc.)</li>
 * <li>The End of Command marker (e)</li>
 * </ul>
 * 
 * <p>
 * The various parts of a command are separated by \n characters. These
 * characters are automatically escaped and unescaped in Strings on both sides
 * (Java and Python).
 * </p>
 * 
 * <p>
 * An output command is usually composed of:
 * </p>
 * <ul>
 * <li>A success or error code (y for yes, x for exception)</li>
 * <li>A return value (e.g., n for null, v for void, or any other value like a
 * String)</li>
 * </ul>
 * 
 * <p>
 * This class should be used only if the user creates new commands.
 * </p>
 * 
 * @author Barthelemy Dagenais
 * 
 */
public class Protocol {

	// TYPES
	public final static char INTEGER_TYPE = 'i';
	public final static char BOOLEAN_TYPE = 'b';
	public final static char DOUBLE_TYPE = 'd';
	public final static char STRING_TYPE = 's';
	public final static char REFERENCE_TYPE = 'r';
	public final static char LIST_TYPE = 'l';
	public final static char SET_TYPE = 'h';
	public final static char ARRAY_TYPE = 't';
	public final static char MAP_TYPE = 'a';
	public final static char NULL_TYPE = 'n';
	public final static char PYTHON_PROXY_TYPE = 'f';

	public final static char PACKAGE_TYPE = 'p';
	public final static char CLASS_TYPE = 'c';
	public final static char METHOD_TYPE = 'm';
	public final static char NO_MEMBER = 'o';
	public final static char VOID = 'v';

	// END OF COMMAND MARKER
	public final static char END = 'e';
	public final static char END_OUTPUT = '\n';

	// OUTPUT VALUES
	public final static char ERROR = 'x';
	public final static char SUCCESS = 'y';

	// SHORTCUT
	public final static String ERROR_COMMAND = "" + ERROR + END_OUTPUT;
	public final static String VOID_COMMAND = "" + SUCCESS + VOID + END_OUTPUT;
	public final static String NO_SUCH_FIELD = "" + SUCCESS + NO_MEMBER
			+ END_OUTPUT;

	// ENTRY POINT
	public final static String ENTRY_POINT_OBJECT_ID = "t";

	// STATIC REFERENCES
	public final static String STATIC_PREFIX = "z:";

	/**
	 * <p>
	 * Assumes that commandPart is <b>not</b> empty.
	 * </p>
	 * 
	 * @param commandPart
	 * @return The boolean value corresponding to this command part.
	 */
	public final static boolean getBoolean(String commandPart) {
		return Boolean.parseBoolean(commandPart.substring(1, commandPart
				.length()));
	}

	/**
	 * <p>
	 * Assumes that commandPart is <b>not</b> empty.
	 * </p>
	 * 
	 * @param commandPart
	 * @return The double value corresponding to this command part.
	 */
	public final static double getDouble(String commandPart) {
		return Double.parseDouble(commandPart
				.substring(1, commandPart.length()));
	}

	/**
	 * <p>
	 * Assumes that commandPart is <b>not</b> empty.
	 * </p>
	 * 
	 * @param commandPart
	 * @return The integer value corresponding to this command part.
	 */
	public final static int getInteger(String commandPart) {
		return Integer.parseInt(commandPart.substring(1, commandPart.length()));
	}

	public final static String getMemberOutputCommand(char memberType) {
		StringBuilder builder = new StringBuilder();

		builder.append(SUCCESS);
		builder.append(memberType);
		builder.append(END_OUTPUT);

		return builder.toString();
	}

	public static String getNoSuchFieldOutputCommand() {
		return NO_SUCH_FIELD;
	}

	/**
	 * <p>
	 * Method provided for consistency. Just returns null.
	 * </p>
	 * 
	 * @param commandPart
	 * @return null.
	 */
	public final static Object getNull(String commandPart) {
		return null;
	}

	public final static Object getObject(String commandPart, Gateway gateway) {
		if (isEmpty(commandPart) || isEnd(commandPart)) {
			throw new Py4JException(
					"Command Part is Empty or is the End of Command Part");
		} else {
			switch (commandPart.charAt(0)) {
			case BOOLEAN_TYPE:
				return getBoolean(commandPart);
			case DOUBLE_TYPE:
				return getDouble(commandPart);
			case INTEGER_TYPE:
				return getInteger(commandPart);
			case NULL_TYPE:
				return getNull(commandPart);
			case VOID:
				return getNull(commandPart);
			case REFERENCE_TYPE:
				return getReference(commandPart, gateway);
			case STRING_TYPE:
				return getString(commandPart);
			case PYTHON_PROXY_TYPE:
				return getPythonProxy(commandPart, gateway);
			default:
				throw new Py4JException("Command Part is unknown.");
			}
		}
	}

	public final static String getOutputCommand(ReturnObject rObject) {
		StringBuilder builder = new StringBuilder();

		if (rObject.isError()) {
			builder.append(ERROR);
		} else {
			builder.append(SUCCESS);
			builder.append(rObject.getCommandPart());
		}
		builder.append(END_OUTPUT);

		return builder.toString();
	}

	public final static String getOutputErrorCommand() {
		return ERROR_COMMAND;
	}

	public final static String getOutputVoidCommand() {
		return VOID_COMMAND;
	}

	public static char getPrimitiveType(Object primitiveObject) {
		char c = INTEGER_TYPE;

		if (primitiveObject instanceof String
				|| primitiveObject instanceof Character) {
			c = STRING_TYPE;
		} else if (primitiveObject instanceof Double
				|| primitiveObject instanceof Float) {
			c = DOUBLE_TYPE;
		} else if (primitiveObject instanceof Boolean) {
			c = BOOLEAN_TYPE;
		}

		return c;
	}

	/**
	 * <p>
	 * Assumes that commandPart is <b>not</b> empty.
	 * </p>
	 * 
	 * @param commandPart
	 * @return A Python proxy specified in this command part.
	 */
	public static Object getPythonProxy(String commandPart, Gateway gateway) {
		String proxyString = commandPart.substring(1, commandPart.length());
		String[] parts = proxyString.split(";");
		int length = parts.length;
		Class<?>[] interfaces = new Class<?>[length - 1];
		if (length < 2) {
			throw new Py4JException("Invalid Python Proxy.");
		}

		for (int i = 1; i < length; i++) {
			try {
				interfaces[i - 1] = Class.forName(parts[i]);
				if (!interfaces[i - 1].isInterface()) {
					throw new Py4JException(
							"This class "
									+ parts[i]
									+ " is not an interface and cannot be used as a Python Proxy.");
				}
			} catch (ClassNotFoundException e) {
				throw new Py4JException("Invalid interface name: " + parts[i]);
			}
		}

		Object proxy = Proxy.newProxyInstance(gateway.getClass()
				.getClassLoader(), interfaces, new PythonProxyHandler(parts[0],
				gateway.getCommunicationChannelFactory(), gateway));

		return proxy;
	}

	/**
	 * <p>
	 * Assumes that commandPart is <b>not</b> empty.
	 * </p>
	 * 
	 * @param commandPart
	 * @return The object referenced in this command part.
	 */
	public final static Object getReference(String commandPart, Gateway gateway) {
		String reference = commandPart.substring(1, commandPart.length());

		if (reference.trim().length() == 0) {
			throw new Py4JException("Reference is empty.");
		}

		return gateway.getObject(reference);
	}
	
	public final static Object getReturnValue(String returnMessage, Gateway gateway) {
		Object returnValue = null;
	
		if (isError(returnMessage)) {
			throw new Py4JException("An exception was raised by the Python Proxy.");
		} else {
			returnValue = getObject(returnMessage.substring(1), gateway);
		}
		
		return returnValue;
	}

	/**
	 * <p>
	 * Assumes that commandPart is <b>not</b> empty.
	 * </p>
	 * 
	 * @param commandPart
	 * @return The reference contained in this command part.
	 */
	public final static String getString(String commandPart) {
		String toReturn = "";
		if (commandPart.length() >= 2) {
			toReturn = StringUtil.unescape(commandPart.substring(1, commandPart
					.length()));
		}
		return toReturn;
	}

	/**
	 * <p>
	 * Assumes that commandPart is <b>not</b> empty.
	 * </p>
	 * 
	 * @param commandPart
	 * @return True if the command part is a boolean
	 */
	public final static boolean isBoolean(String commandPart) {
		return commandPart.charAt(0) == BOOLEAN_TYPE;
	}

	/**
	 * <p>
	 * Assumes that commandPart is <b>not</b> empty.
	 * </p>
	 * 
	 * @param commandPart
	 * @return True if the command part is a double
	 */
	public final static boolean isDouble(String commandPart) {
		return commandPart.charAt(0) == DOUBLE_TYPE;
	}

	public final static boolean isEmpty(String commandPart) {
		return commandPart == null || commandPart.trim().length() == 0;
	}

	/**
	 * <p>
	 * Assumes that commandPart is <b>not</b> empty.
	 * </p>
	 * 
	 * @param commandPart
	 * @return True if the command part is the end token
	 */
	public final static boolean isEnd(String commandPart) {
		return commandPart.length() == 1 && commandPart.charAt(0) == 'e';
	}

	/**
	 * <p>
	 * Assumes that commandPart is <b>not</b> null.
	 * </p>
	 * 
	 * @param returnMessage
	 * @return True if the return message is an error
	 */
	public final static boolean isError(String returnMessage) {
		return returnMessage.length() == 0 || returnMessage.charAt(0) == ERROR;
	}

	/**
	 * <p>
	 * Assumes that commandPart is <b>not</b> empty.
	 * </p>
	 * 
	 * @param commandPart
	 * @return True if the command part is an integer
	 */
	public final static boolean isInteger(String commandPart) {
		return commandPart.charAt(0) == INTEGER_TYPE;
	}

	/**
	 * <p>
	 * Assumes that commandPart is <b>not</b> empty.
	 * </p>
	 * 
	 * @param commandPart
	 * @return True if the command part is null
	 */
	public final static boolean isNull(String commandPart) {
		return commandPart.charAt(0) == NULL_TYPE;
	}

	/**
	 * <p>
	 * Assumes that commandPart is <b>not</b> empty.
	 * </p>
	 * 
	 * @param commandPart
	 * @return True if the command part is a python proxy
	 */
	public final static boolean isPythonProxy(String commandPart) {
		return commandPart.charAt(0) == PYTHON_PROXY_TYPE;
	}

	/**
	 * <p>
	 * Assumes that commandPart is <b>not</b> empty.
	 * </p>
	 * 
	 * @param commandPart
	 * @return True if the command part is a reference
	 */
	public final static boolean isReference(String commandPart) {
		return commandPart.charAt(0) == REFERENCE_TYPE;
	}

	/**
	 * <p>
	 * Assumes that commandPart is <b>not</b> empty.
	 * </p>
	 * 
	 * @param commandPart
	 * @return True if the command part is a reference
	 */
	public final static boolean isString(String commandPart) {
		return commandPart.charAt(0) == STRING_TYPE;
	}
}
