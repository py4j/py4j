package py4j.reflection;

import org.junit.Test;

import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

public class ReflectionUtilTest {

	@Test
	public void testRootClassLoading() {
		try {
			ReflectionUtil.setClassLoadingStrategy(
					new RootClassLoadingStrategy());
			Class stringClass = ReflectionUtil.classForName("java.lang" +
					".String");
			Object obj = stringClass.newInstance();
			assertTrue(obj instanceof String);
		} catch (Exception e) {
			fail();
		}
	}

	@Test
	public void testCurrentThreadClassLoading() {
		try {
			ReflectionUtil.setClassLoadingStrategy(
					new CurrentThreadClassLoadingStrategy());
			Class stringClass = ReflectionUtil.classForName("java.lang" +
					".String");
			Object obj = stringClass.newInstance();
			assertTrue(obj instanceof String);
		} catch (Exception e) {
			fail();
		}
	}
}
