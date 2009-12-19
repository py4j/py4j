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
	
	@Test
	public void testCount() {
		String inputCommand = ListCommand.LIST_COUNT_COMMAND + "\n" + target + "\ns1\ne\n";
		list.add("1");
		try {
			command.execute("l", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yi2", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
	
	@SuppressWarnings("unchecked")
	@Test
	public void testConcat() {
		String inputCommand = ListCommand.LIST_CONCAT_COMMAND + "\n" + target + "\n" + target2 + "\ne\n";
		try {
			// concat l + l2
			command.execute("l", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("ylo2", sWriter.toString());
			List newList = (List)gateway.getObject("o2");
			assertEquals(7, newList.size());
			assertEquals(4, list.size());
			assertEquals(3, list2.size());
			assertEquals(newList.get(4),list2.get(0));
			
			// concat l + l
			inputCommand = ListCommand.LIST_CONCAT_COMMAND + "\n" + target + "\n" + target + "\ne\n";
			command.execute("l", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("ylo2ylo3", sWriter.toString());
			newList = (List)gateway.getObject("o3");
			assertEquals(8, newList.size());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
	
	@SuppressWarnings("unchecked")
	@Test
	public void testMult() {
		String inputCommand = ListCommand.LIST_MULT_COMMAND + "\n" + target + "\ni3\ne\n";
		try {
			// l3 = l1 * 3
			command.execute("l", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("ylo2", sWriter.toString());
			List newList = (List)gateway.getObject("o2");
			assertEquals(12, newList.size());
			assertEquals(4, list.size());
			
			// l3 = l1 * -1
			inputCommand = ListCommand.LIST_MULT_COMMAND + "\n" + target + "\ni-1\ne\n";
			command.execute("l", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("ylo2ylo3", sWriter.toString());
			newList = (List)gateway.getObject("o3");
			assertEquals(0, newList.size());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
	
	@Test
	public void testiMult() {
		String inputCommand = ListCommand.LIST_IMULT_COMMAND + "\n" + target + "\ni3\ne\n";
		try {
			// l *= 3
			assertEquals(4, list.size());
			command.execute("l", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yn", sWriter.toString());
			assertEquals(12, list.size());
			
			// l *= -1
			inputCommand = ListCommand.LIST_IMULT_COMMAND + "\n" + target + "\ni-1\ne\n";
			command.execute("l", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("ynyn", sWriter.toString());
			assertEquals(0, list.size());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
	
	@SuppressWarnings("unchecked")
	@Test
	public void testSlice() {
		String inputCommand = ListCommand.LIST_SLICE_COMMAND + "\n" + target + "\ni1\ni2\ne\n";
		try {
			// l3 = l1[1:3]
			command.execute("l", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("ylo2", sWriter.toString());
			List newList = (List)gateway.getObject("o2");
			assertEquals(2, newList.size());
			assertEquals("9",newList.get(0));
			assertEquals("3",newList.get(1));
			assertEquals(4, list.size());
			
			// l3 = l[0:0]
			inputCommand = ListCommand.LIST_SLICE_COMMAND + "\n" + target + "\ne\n";
			command.execute("l", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("ylo2ylo3", sWriter.toString());
			newList = (List)gateway.getObject("o3");
			assertEquals(0, newList.size());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
}

