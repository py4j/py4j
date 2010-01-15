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

public class ReflectionCommandTest {
	private Gateway gateway;
	private ReflectionCommand command;
	private BufferedWriter writer;
	private StringWriter sWriter;
	
	@Before
	public void setUp() {
		gateway = new Gateway(new ExampleEntryPoint());
		gateway.startup();
		command = new ReflectionCommand();
		command.init(gateway);
		sWriter = new StringWriter();
		writer = new BufferedWriter(sWriter);
		
	}

	@After
	public void tearDown() {
		gateway.shutdown();
	}
	
	@Test
	public void testUnknown() {
		String inputCommand1 = ReflectionCommand.GET_UNKNOWN_SUB_COMMAND_NAME + "\n" + "java" + "\ne\n";
		String inputCommand2 = ReflectionCommand.GET_UNKNOWN_SUB_COMMAND_NAME + "\n" + "java.lang" + "\ne\n";
		String inputCommand3 = ReflectionCommand.GET_UNKNOWN_SUB_COMMAND_NAME + "\n" + "java.lang.String" + "\ne\n";
		String inputCommand4 = ReflectionCommand.GET_UNKNOWN_SUB_COMMAND_NAME + "\n" + "p1.Cat" + "\ne\n";
		try {
			command.execute("r", new BufferedReader(new StringReader(
					inputCommand1)), writer);
			assertEquals("yp", sWriter.toString());
			command.execute("r", new BufferedReader(new StringReader(
					inputCommand2)), writer);
			assertEquals("ypyp", sWriter.toString());
			command.execute("r", new BufferedReader(new StringReader(
					inputCommand3)), writer);
			assertEquals("ypypyc", sWriter.toString());
			command.execute("r", new BufferedReader(new StringReader(
					inputCommand4)), writer);
			assertEquals("ypypycyc", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
	
	@Test
	public void testMember() {
		String inputCommand1 = ReflectionCommand.GET_MEMBER_SUB_COMMAND_NAME + "\n" + "java.lang.String\n" + "valueOf"  + "\ne\n";
		String inputCommand2 = ReflectionCommand.GET_MEMBER_SUB_COMMAND_NAME + "\n" + "java.lang.String\n" + "length"  + "\ne\n";
		String inputCommand3 = ReflectionCommand.GET_MEMBER_SUB_COMMAND_NAME + "\n" + "p1.Cat\n" + "meow"  + "\ne\n";
		String inputCommand4 = ReflectionCommand.GET_MEMBER_SUB_COMMAND_NAME + "\n" + "p1.Cat\n" + "meow20"  + "\ne\n"; // does not exist
		String inputCommand5 = ReflectionCommand.GET_MEMBER_SUB_COMMAND_NAME + "\n" + "p1.Cat\n" + "meow15"  + "\ne\n";
		String inputCommand6 = ReflectionCommand.GET_MEMBER_SUB_COMMAND_NAME + "\n" + "p1.Cat\n" + "CONSTANT"  + "\ne\n";
		try {
			command.execute("r", new BufferedReader(new StringReader(
					inputCommand1)), writer);
			assertEquals("ym", sWriter.toString());
			command.execute("r", new BufferedReader(new StringReader(
					inputCommand2)), writer);
			assertEquals("ymx", sWriter.toString());
			command.execute("r", new BufferedReader(new StringReader(
					inputCommand3)), writer);
			assertEquals("ymxx", sWriter.toString());
			command.execute("r", new BufferedReader(new StringReader(
					inputCommand4)), writer);
			assertEquals("ymxxx", sWriter.toString());
			command.execute("r", new BufferedReader(new StringReader(
					inputCommand5)), writer);
			assertEquals("ymxxxym", sWriter.toString());
			command.execute("r", new BufferedReader(new StringReader(
					inputCommand6)), writer);
			assertEquals("ymxxxymysSalut!", sWriter.toString());
		} catch(Exception e) {
			e.printStackTrace();
			fail();
		}
		
	}
}
