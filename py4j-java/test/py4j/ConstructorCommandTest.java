package py4j;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.StringReader;
import java.io.StringWriter;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import py4j.examples.ExampleEntryPoint;
import py4j.examples.Stack;

public class ConstructorCommandTest {
	private ExampleEntryPoint entryPoint;
	private Gateway gateway;
	private ConstructorCommand command;
	private BufferedWriter writer;
	private StringWriter sWriter;

	@Before
	public void setUp() {
		entryPoint = new ExampleEntryPoint();
		gateway = new Gateway(entryPoint);
		gateway.startup();
		command = new ConstructorCommand();
		command.init(gateway);
		sWriter = new StringWriter();
		writer = new BufferedWriter(sWriter);
	}

	@After
	public void tearDown() {
		gateway.shutdown();
	}
	
	@Test
	public void testConstructor0Arg() {
		String inputCommand = "py4j.examples.ExampleClass\ne\n";
		try {
			command.execute("i", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yro0", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
	
	@Test
	public void testConstructor1Arg() {
		String inputCommand = "py4j.examples.ExampleClass\ni5\ne\n";
		try {
			command.execute("i", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yro0", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
	
	@Test
	public void testDefaultConstructor() {
		String inputCommand = "py4j.examples.Stack\ne\n";
		try {
			command.execute("i", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yro0", sWriter.toString());
			assertTrue(gateway.getObject("o0") instanceof Stack);
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
	
	@Test
	public void testWrongConstructor() {
		String inputCommand = "py4j.examples.Stack\ni5\ne\n";
		try {
			command.execute("i", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("x", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
}
