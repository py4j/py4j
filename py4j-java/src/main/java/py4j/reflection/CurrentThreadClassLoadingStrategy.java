package py4j.reflection;

/**
 * <p>This class loading strategy uses the current thread's ClassLoader to
 * load a class from a fully qualified name.</p>
 */
public class CurrentThreadClassLoadingStrategy implements ClassLoadingStrategy {

	@Override
	public Class<?> classForName(String className) throws ClassNotFoundException {
		ClassLoader classLoader = Thread.currentThread().getContextClassLoader();
		return Class.forName(className, true, classLoader);
	}
}
