package py4j.reflection;

/**
 * <p>This class loading strategy just uses the root ClassLoader
 * to load a class from a fully qualified name.</p>
 */
public class RootClassLoadingStrategy implements ClassLoadingStrategy {

	@Override
	public Class<?> classForName(String className) throws
			ClassNotFoundException {
		return Class.forName(className);
	}
}
