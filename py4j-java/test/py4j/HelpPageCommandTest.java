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

public class HelpPageCommandTest {
	private ExampleEntryPoint entryPoint;
	private Gateway gateway;
	private HelpPageCommand command;
	private BufferedWriter writer;
	private StringWriter sWriter;
	private String target;

	@Before
	public void setUp() {
		entryPoint = new ExampleEntryPoint();
		gateway = new Gateway(entryPoint);
		gateway.startup();
		command = new HelpPageCommand();
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
	public void testHelpObject() {
		String inputCommand = "o\n" + target + "\ntrue\ne\n";
		try {
			assertTrue(gateway.getBindings().containsKey(target));
			command.execute("h", new BufferedReader(new StringReader(
					inputCommand)), writer);
			String page = sWriter.toString();
			System.out.println(page);
			assertEquals(827,page.length());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
	
	@Test
	public void testHelpClass() {
		String inputCommand = "c\njava.lang.String\ntrue\ne\n";
		try {
			assertTrue(gateway.getBindings().containsKey(target));
			command.execute("h", new BufferedReader(new StringReader(
					inputCommand)), writer);
			String page = sWriter.toString();
			System.out.println(page);
			assertEquals(3405,page.length());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
}
