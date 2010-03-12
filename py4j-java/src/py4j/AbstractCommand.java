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

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

public abstract class AbstractCommand implements Command {

	protected Gateway gateway;
	
	private final Logger logger = Logger.getLogger(AbstractCommand.class.getName());

	@Override
	public abstract void execute(String commandName, BufferedReader reader,
			BufferedWriter writer) throws Py4JException, IOException;

	@Override
	public void init(Gateway gateway) {
		this.gateway = gateway;
	}

	protected List<String> getStringArguments(BufferedReader reader) throws IOException {
		List<String> arguments = new ArrayList<String>();
		String line = reader.readLine();

		while (!Protocol.isEmpty(line) && !Protocol.isEnd(line)) {
			logger.info("Raw String Argument: " + line);
			arguments.add(line);
			line = reader.readLine();
		}

		return arguments;
	}
	
	protected List<Argument> getArguments(BufferedReader reader)
			throws IOException {
		List<Argument> arguments = new ArrayList<Argument>();
		List<String> stringArguments = getStringArguments(reader);
		
		for (String stringArgument : stringArguments) {
			Argument argument = new Argument(Protocol.getObject(stringArgument), Protocol
					.isReference(stringArgument));
			arguments.add(argument);
		}

		return arguments;
	}

	protected ReturnObject invokeMethod(String methodName,
			String targetObjectId, List<Argument> arguments) {
		ReturnObject returnObject = null;
		try {
			returnObject = gateway
					.invoke(methodName, targetObjectId, arguments);
		} catch (Exception e) {
			logger.log(Level.INFO, "Received exception while executing this command: " + methodName, e);
			returnObject = ReturnObject.getErrorReturnObject();
		}
		return returnObject;
	}

}
