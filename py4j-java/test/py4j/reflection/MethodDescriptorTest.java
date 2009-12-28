package py4j.reflection;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.fail;

import org.junit.Test;

import p1.Cat;

public class MethodDescriptorTest {

	@Test
	public void testInternalRepresentation() {
		try {
			MethodDescriptor mDesc1 = new MethodDescriptor("meowmeow",
					Cat.class, new Class[] { String.class });
			MethodDescriptor mDesc2 = new MethodDescriptor(Cat.class.getMethod(
					"meowmeow", new Class[] { String.class }));
			assertEquals(mDesc1, mDesc2);
			assertEquals(mDesc1.hashCode(), mDesc2.hashCode());
			assertEquals(mDesc1.getInternalRepresentation(),"p1.Cat.meowmeow(java.lang.String.)");

		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

}
