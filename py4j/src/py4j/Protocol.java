/*******************************************************************************
 * 
 * Copyright (c) 2009, Barthelemy Dagenais All rights reserved.
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

/**
 * <p>
 * This class defines the protocol used to communicate between two virtual
 * machines (e.g., Python and Java).
 * </p>
 * <p>
 * Currently, the protocol requires type information (e.g., is this string an
 * integer, an object reference or a boolean?) to be embedded within a command.
 * The rational is that the source virtual machine is usually better at
 * determining the type of objects it sends.
 * </p>
 * <p>
 * There are two protocols defined in this class. The <em>input</em> protocol
 * defines the command parts expected to be received by the Java gateway. The
 * <em>output</em> protocol adds the command parts that can be sent to the
 * source virtual machine (e.g., an error has occurred while executing a
 * command).
 * </p>
 * <p>
 * <b>TODO:</b>Implement a protocol that discovers the type of parameters in a
 * command. This might be more efficient if the protocol is ever used by weakly
 * typed languages.
 * </p>
 * 
 * @author Barthelemy Dagenais
 * 
 */
public class Protocol {

	// INPUT PROTOCOL
	public final static char INTEGER_TYPE = 'i';
	public final static char BOOLEAN_TYPE = 'b';
	public final static char DOUBLE_TYPE = 'd';
	public final static char STRING_TYPE = 's';
	public final static char REFERENCE_TYPE = 'r';
	public final static char LIST_TYPE = 'l';
	public final static char NULL_TYPE = 'n';
	public final static char END = 'e';
	

	// OUTPUT PROTOCOL
	public final static char ERROR = 'x';
	public final static char SUCCESS = 'y';

	public final static boolean isEmpty(String commandPart) {
		return commandPart == null || commandPart.trim().length() == 0;
	}

	/**
	 * <p>
	 * Assumes that commandPart is <b>not</b> empty.
	 * </p>
	 * 
	 * @param commandPart
	 * @return
	 */
	public final static boolean isEnd(String commandPart) {
		return commandPart.length() == 1 && commandPart.charAt(0) == 'e';
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
	 * @return The integer value corresponding to this command part.
	 */
	public final static int getInteger(String commandPart) {
		return Integer.parseInt(commandPart.substring(1, commandPart.length()));
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
	 * @return True if the command part is a double
	 */
	public final static boolean isDouble(String commandPart) {
		return commandPart.charAt(0) == DOUBLE_TYPE;
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
	 * @return The reference contained in this command part.
	 */
	public final static String getReference(String commandPart) {
		String reference = commandPart.substring(1, commandPart.length());

		if (reference.trim().length() == 0) {
			throw new Py4JException("Reference is empty.");
		}

		return reference;
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
	 * @return True if the command part is null
	 */
	public final static boolean isNull(String commandPart) {
		return commandPart.charAt(0) == NULL_TYPE;
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

	public final static Object getObject(String commandPart) {
		if (isEmpty(commandPart) || isEnd(commandPart)) {
			throw new Py4JException(
					"Command Part is Empty or is the End Command Part");
		} else if (isReference(commandPart)) {
			return getReference(commandPart);
		} else if (isInteger(commandPart)) {
			return getInteger(commandPart);
		} else if (isBoolean(commandPart)) {
			return getBoolean(commandPart);
		} else if (isDouble(commandPart)) {
			return getDouble(commandPart);
		} else if (isString(commandPart)) {
			return getString(commandPart);
		} else if (isNull(commandPart)) {
			return getNull(commandPart);
		} else {
			throw new Py4JException("Command Part is unknown.");
		}
	}

	public final static String getOutputCommand(ReturnObject rObject) {
		StringBuilder builder = new StringBuilder();

		if (rObject.isError()) {
			builder.append(ERROR);
		} else {
			builder.append(SUCCESS);
			if (rObject.isNull()) {
				builder.append(NULL_TYPE);
			} else if (rObject.isList()) {
				builder.append(LIST_TYPE);
				builder.append(rObject.getName());
			} else if (rObject.isReference()) {
				// TODO Handle list, map, etc.
				builder.append(REFERENCE_TYPE);
				builder.append(rObject.getName());
			} else {
				Object primitiveObject = rObject.getPrimitiveObject();
				builder.append(getPrimitiveType(primitiveObject));
				builder.append(primitiveObject.toString());
			}
		}

		return builder.toString();
	}

	private static char getPrimitiveType(Object primitiveObject) {
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
}
