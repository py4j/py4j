package py4j.reflection;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public class TypeConverterTest {

	@Test
	public void testTypeConversion() {
		TypeConverter converter = new TypeConverter();
		assertEquals("test",converter.convert("test"));
		assertTrue(converter.convert("test") instanceof String);
	}
	
	@Test
	public void testDoubleConversion() {
		TypeConverter converter = new TypeConverter(TypeConverter.DOUBLE_TO_FLOAT);
		assertEquals(1.2f,converter.convert(1.2));
		assertTrue(converter.convert(1.2) instanceof Float);
	}
	
	@Test
	public void testIntConversion() {
		TypeConverter converter = new TypeConverter(TypeConverter.INT_TO_SHORT);
		assertEquals((short)100, converter.convert(100));
		assertTrue(converter.convert(100) instanceof Short);
		
		converter = new TypeConverter(TypeConverter.INT_TO_BYTE);
		assertEquals((byte)100, converter.convert(100));
		assertTrue(converter.convert(102) instanceof Byte);
	}
	
	@Test
	public void testStringConversion() {
		TypeConverter converter = new TypeConverter(TypeConverter.STRING_TO_CHAR);
		assertEquals('c', converter.convert("c"));
		assertTrue(converter.convert("c") instanceof Character);
	}
}
