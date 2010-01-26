package py4j;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
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
		command.init(gateway);
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
			command.execute("m", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yv", sWriter.toString());
			assertFalse(gateway.getBindings().containsKey(target));
			command.execute("m", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yvyv", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
	
	@Test
	public void testAttach() {
		String inputCommand = "a\n" + target + "\ne\n";
		try {
			assertTrue(gateway.getBindings().containsKey(target));
			command.execute("m", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yro1", sWriter.toString());
			assertTrue(gateway.getBindings().containsKey(target));
			assertTrue(gateway.getBindings().containsKey("o1"));
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
}
