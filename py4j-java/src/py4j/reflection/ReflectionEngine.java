package py4j.reflection;

import java.lang.reflect.Field;
import java.lang.reflect.Method;

public class ReflectionEngine {

	private final LRUCache<MethodDescriptor, Method> cache;
	
	public ReflectionEngine() {
		this(new LRUCache<MethodDescriptor, Method>());
	}
	
	public ReflectionEngine(LRUCache<MethodDescriptor, Method> cache) {
		this.cache = cache;
	}
	
	public Field getField() {
		return null;
	}
	
	public Method getMethod() {
		return null;
	}
	
	public Object getFieldValue() {
		return null;
	}
	
	public Object invokeMethod() {
		return null;
	}
	
}
