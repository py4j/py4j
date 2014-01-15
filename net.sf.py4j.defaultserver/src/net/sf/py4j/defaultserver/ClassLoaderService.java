package net.sf.py4j.defaultserver;

/**
 * This defines an interface to service that provides a class loader 
 */
public interface ClassLoaderService {

	public static final String SERVICE_NAME = ClassLoaderService.class.getName();

	/**
	 * @return a class loader
	 */
	public ClassLoader getClassLoader();
}
