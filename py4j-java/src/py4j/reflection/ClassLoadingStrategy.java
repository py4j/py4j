package py4j.reflection;

/**
 * <p>Strategy interface to load a class from a fully qualified name.</p>
 */
public interface ClassLoadingStrategy {

	Class<?> classForName(String className) throws
			ClassNotFoundException;
}
