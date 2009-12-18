package py4j;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.fail;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.StringReader;
import java.io.StringWriter;
import java.util.ArrayList;
import java.util.List;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import py4j.examples.ExampleGateway;

public class ListCommandTest {
	
	private ExampleGateway gateway;
	private ListCommand command;
	private BufferedWriter writer;
	private StringWriter sWriter;
	private String target;
	private String target2;
	private List<String> list;
	private List<Thread> list2;
	
	@Before
	public void setUp() {
		gateway = new ExampleGateway();
		gateway.startup();
		command = new ListCommand();
		command.init(gateway);
		sWriter = new StringWriter();
		writer = new BufferedWriter(sWriter);
		
		list = new ArrayList<String>();
		list.add("1");
		list.add("9");
		list.add("3");
		list.add("2");
		list2 = new ArrayList<Thread>();
		list2.add(new Thread());
		list2.add(new Thread());
		list2.add(new Thread());
		target = gateway.putNewObject(list);
		target2 = gateway.putNewObject(list2);
	}

	@After
	public void tearDown() {
		gateway.shutdown();
	}
	
	@Test
	public void testSort() {
		String inputCommand = ListCommand.LIST_SORT_COMMAND + "\n" + target + "\ne\n";
		try {
			command.execute("l", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yn", sWriter.toString());
			assertEquals(list.get(0), "1");
			assertEquals(list.get(3), "9");
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
	
	@Test
	public void testSortException() {
		String inputCommand = ListCommand.LIST_SORT_COMMAND + "\n" + target2 + "\ne\n";
		try {
			command.execute("l", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("x", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
	
	@Test
	public void testReverse() {
		String inputCommand = ListCommand.LIST_REVERSE_COMMAND + "\n" + target + "\ne\n";
		try {
			command.execute("l", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yn", sWriter.toString());
			assertEquals(list.get(0), "2");
			assertEquals(list.get(1), "3");
			assertEquals(list.get(2), "9");
			assertEquals(list.get(3), "1");
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
	
	@Test
	public void testReverseException() {
		String inputCommand = ListCommand.LIST_REVERSE_COMMAND + "\n" + target2 + "\ne\n";
		try {
			command.execute("l", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yn", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
	
	@Test
	public void testMin() {
		String inputCommand = ListCommand.LIST_MIN_COMMAND + "\n" + target + "\ne\n";
		try {
			command.execute("l", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("ys1", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
	
	@Test
	public void testMinException() {
		String inputCommand = ListCommand.LIST_MIN_COMMAND + "\n" + target2 + "\ne\n";
		try {
			command.execute("l", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("x", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
	
	@Test
	public void testMax() {
		String inputCommand = ListCommand.LIST_MAX_COMMAND + "\n" + target + "\ne\n";
		try {
			command.execute("l", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("ys9", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
	
	@Test
	public void testMaxException() {
		String inputCommand = ListCommand.LIST_MAX_COMMAND + "\n" + target2 + "\ne\n";
		try {
			command.execute("l", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("x", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
}

