/******************************************************************************
 * Copyright (c) 2009-2022, Barthelemy Dagenais and individual contributors.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * - Redistributions of source code must retain the above copyright notice,
 * this list of conditions and the following disclaimer.
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
 *****************************************************************************/
package py4j.commands;

import static org.junit.Assert.*;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.StringReader;
import java.io.StringWriter;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import py4j.Gateway;
import py4j.examples.ExampleEntryPoint;

public class MemoryCommandTest {
	private ExampleEntryPoint entryPoint;
	private Gateway gateway;
	private MemoryCommand command;
	private BufferedWriter writer;
	private StringWriter sWriter;
	private String target;

	@Before
	public void setUp() {
		entryPoint = new ExampleEntryPoint();
		gateway = new Gateway(entryPoint);
		gateway.startup();
		command = new MemoryCommand();
		command.init(gateway, null);
		sWriter = new StringWriter();
		writer = new BufferedWriter(sWriter);
		target = gateway.getReturnObject(entryPoint.getNewExample()).getName();
	}

	@After
	public void tearDown() {
		gateway.shutdown();
	}

	@Test
	public void testDelete() {
		String inputCommand = "d\n" + target + "\ne\n";
		try {
			assertTrue(gateway.getBindings().containsKey(target));
			command.execute("m", new BufferedReader(new StringReader(inputCommand)), writer);
			assertEquals("!yv\n", sWriter.toString());
			assertFalse(gateway.getBindings().containsKey(target));
			command.execute("m", new BufferedReader(new StringReader(inputCommand)), writer);
			assertEquals("!yv\n!yv\n", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

}
