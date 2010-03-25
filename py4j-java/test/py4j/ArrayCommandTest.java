package py4j;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.fail;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.StringReader;
import java.io.StringWriter;
import java.lang.reflect.Array;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import py4j.examples.ExampleEntryPoint;

public class ArrayCommandTest {
	private Gateway gateway;
	private ArrayCommand command;
	private BufferedWriter writer;
	private StringWriter sWriter;
	private String target;
	private String target2;
	private Object array1;
	private Object array2;

	@Before
	public void setUp() {
		gateway = new Gateway(new ExampleEntryPoint());
		gateway.startup();
		command = new ArrayCommand();
		command.init(gateway);
		sWriter = new StringWriter();
		writer = new BufferedWriter(sWriter);
		array1 = new String[] { "222", "111" };
		array2 = new int[] { 2, 1 };
		target = gateway.putNewObject(array1);
		target2 = gateway.putNewObject(array2);
	}

	@After
	public void tearDown() {
		gateway.shutdown();
	}

	@Test
	public void testGet() {
		String inputCommand = ArrayCommand.ARRAY_GET_SUB_COMMAND_NAME + "\n"
				+ target + "\ni1\ne\n";
		try {
			command.execute("a", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("ys111\n", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testSet() {
		String inputCommand = ArrayCommand.ARRAY_SET_SUB_COMMAND_NAME + "\n"
				+ target2 + "\ni1\ni555\ne\n";
		try {
			command.execute("a", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yv\n", sWriter.toString());
			assertEquals(Array.getInt(array2, 1), 555);
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testLength() {
		String inputCommand = ArrayCommand.ARRAY_LEN_SUB_COMMAND_NAME + "\n"
				+ target + "\ne\n";
		try {
			command.execute("a", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yi2\n", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testCreateArray() {
		String inputCommand = ArrayCommand.ARRAY_CREATE_SUB_COMMAND_NAME
				+ "\nsint\ni3\ne\n";
		try {
			command.execute("a", new BufferedReader(new StringReader(
					inputCommand)), writer);
			int[] intarray = (int[]) gateway.getObject("o2");
			assertEquals(3, intarray.length);

			inputCommand = ArrayCommand.ARRAY_CREATE_SUB_COMMAND_NAME
					+ "\nsjava.lang.String\ni3\ni5\ne\n";
			command.execute("a", new BufferedReader(new StringReader(
					inputCommand)), writer);
			String[][] stringarray = (String[][]) gateway.getObject("o3");
			assertEquals(3, stringarray.length);
			assertEquals(5, stringarray[0].length);
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testSlice() {
		int[] array3 = new int[] { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 };
		String[][] array4 = new String[][] { { "111", "222" },
				{ "aaa", "bbb" }, { "88", "99" } };
		gateway.putNewObject(array3);
		gateway.putNewObject(array4);
		String inputCommand = ArrayCommand.ARRAY_SLICE_SUB_COMMAND_NAME + "\n"
				+ "o2" + "\ni1\ni5\ne\n";
		try {
			command.execute("a", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yto4\n", sWriter.toString());
			int[] intarray = (int[]) gateway.getObject("o4");
			assertEquals(2, intarray.length);
			assertEquals(6,intarray[1]);
			
			inputCommand = ArrayCommand.ARRAY_SLICE_SUB_COMMAND_NAME + "\n"
			+ "o3" + "\ni2\ne\n";
			command.execute("a", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yto4\nyto5\n", sWriter.toString());
			String[][] stringarray = (String[][])gateway.getObject("o5");
			assertEquals(1, stringarray.length);
			assertEquals("99",stringarray[0][1]);
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}

	}

	@Test
	public void testArrayType() {
		ReturnObject rObject = ReturnObject.getArrayReturnObject(target, 2);
		assertEquals("yt" + target + "\n", Protocol.getOutputCommand(rObject));
	}
}
