package py4j.reflection;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

import java.lang.reflect.Method;

import org.junit.Test;

import p1.Cat;

public class MethodInvokerTest {

	@Test
	public void testInvoke() {
		Cat cat = new Cat();
		try {
			Method m = Cat.class.getMethod("meow10", float.class);
			MethodInvoker invoker = new MethodInvoker(m, new TypeConverter[] {new TypeConverter(TypeConverter.DOUBLE_TO_FLOAT)}, 0);
			invoker.invoke(cat, new Object[] {new Double(2.0)});
			
			m = Cat.class.getMethod("meow11", new Class[0]);
			invoker = new MethodInvoker(m, null, 0);
			invoker.invoke(cat, new Object[0]);
			
			m = Cat.class.getMethod("meow10", float.class);
			invoker = new MethodInvoker(m, null, 0);
			invoker.invoke(cat, new Object[] {new Float(1.1f)});
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
	
	@Test
	public void testVoid() {
		try {
			Method m = Cat.class.getMethod("meow10", float.class);
			MethodInvoker invoker = new MethodInvoker(m, new TypeConverter[] {new TypeConverter(TypeConverter.DOUBLE_TO_FLOAT)}, 0);
			assertTrue(invoker.isVoid());
			
			m = Cat.class.getMethod("meow12", new Class[0]);
			invoker = new MethodInvoker(m, null, 0);
			assertFalse(invoker.isVoid());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

}
