package py4j;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.fail;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.StringReader;
import java.io.StringWriter;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import py4j.examples.ExampleEntryPoint;

public class FieldCommandTest {
	private ExampleEntryPoint entryPoint;
	private Gateway gateway;
	private FieldCommand command;
	private BufferedWriter writer;
	private StringWriter sWriter;
	private String target;

	@Before
	public void setUp() {
		entryPoint = new ExampleEntryPoint();
		gateway = new Gateway(entryPoint);
		gateway.startup();
		command = new FieldCommand();
		command.init(gateway);
		sWriter = new StringWriter();
		writer = new BufferedWriter(sWriter);
		target = gateway.putNewObject(entryPoint.getNewExample());
	}

	@After
	public void tearDown() {
		gateway.shutdown();
	}
	
	@Test
	public void testNoMember() {
		String inputCommand = "g\n" + target + "\nfield2\ne\n";
		try {
			command.execute("f", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yo", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
	
	@Test
	public void testPrimitive() {
		String inputCommand = "g\n" + target + "\nfield10\ne\n";
		try {
			command.execute("f", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yi10", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
	
	@Test
	public void testObject() {
		String inputCommand = "g\n" + target + "\nfield20\ne\n";
		try {
			command.execute("f", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yro1", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
	
	@Test
	public void testNull() {
		String inputCommand = "g\n" + target + "\nfield21\ne\n";
		try {
			command.execute("f", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yn", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
}
