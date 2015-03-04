/**
 * Copyright (c) 2015, Jonah Graham All rights reserved.
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
 */

package py4j.commands;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.util.logging.Logger;

import py4j.Gateway;
import py4j.Protocol;
import py4j.Py4JException;
import py4j.ReturnObject;
import py4j.reflection.ReflectionEngine;

public class DirCommand extends AbstractCommand {

	private final Logger logger = Logger.getLogger(DirCommand.class.getName());

	private ReflectionEngine reflectionEngine;

	public static final String DIR_COMMAND_NAME = "d";
	public static final String DIR_FIELDS_SUBCOMMAND_NAME = "f";
	public static final String DIR_METHODS_SUBCOMMAND_NAME = "m";

	public DirCommand() {
		this.commandName = DIR_COMMAND_NAME;
	}

	@Override
	public void execute(String commandName, BufferedReader reader,
			BufferedWriter writer) throws Py4JException, IOException {
		String subCommand = reader.readLine();
		Object targetObject = gateway.getObject(reader.readLine());
		final String[] names;
		if (subCommand.equals(DIR_FIELDS_SUBCOMMAND_NAME)) {
			names = reflectionEngine.getPublicFieldNames(targetObject);
		} else { // if (subCommand.equals(DIR_METHODS_SUBCOMMAND_NAME))
			names = reflectionEngine.getPublicMethodNames(targetObject);
		}

		// Read and discard end of command
		reader.readLine();

		StringBuilder namesJoinedBuilder = new StringBuilder();
		for (String name : names) {
			namesJoinedBuilder.append(name);
			namesJoinedBuilder.append("\n");
		}
		final String namesJoined;
		if (namesJoinedBuilder.length() > 0) {
			namesJoined = namesJoinedBuilder.substring(0, namesJoinedBuilder.length() - 1);
		} else {
			namesJoined = "";
		}

		ReturnObject returnObject = gateway.getReturnObject(namesJoined);
		String returnCommand = Protocol.getOutputCommand(returnObject);
		logger.finest("Returning command: " + returnCommand);
		writer.write(returnCommand);
		writer.flush();
	}

	@Override
	public void init(Gateway gateway) {
		super.init(gateway);
		reflectionEngine = gateway.getReflectionEngine();
	}

}
