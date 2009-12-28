package py4j.reflection;

import java.lang.reflect.Method;

@SuppressWarnings("unchecked")
public class MethodDescriptor {

	private String internalRepresentation;
	
	private Method method;
	
	private String name;
	
	private Class container;
	
	private Class[] actualParameters;
	
	private final char DOT = '.';

	public MethodDescriptor(Method method) {
		this.method = method;
		this.internalRepresentation = buildInternalRepresentation(method.getDeclaringClass(), method.getName(), method.getParameterTypes());
	}

	public MethodDescriptor(String name, Class container,
			Class[] actualParameters) {
		super();
		this.name = name;
		this.container = container;
		this.actualParameters = actualParameters;
		this.internalRepresentation = buildInternalRepresentation(container, name, actualParameters);
	}
	
	private String buildInternalRepresentation(Class container, String name, Class[] params) {
		StringBuilder builder = new StringBuilder();
		
		builder.append(container.getName());
		builder.append(DOT);
		builder.append(name);
		builder.append('(');
		for (Class param : params) {
			builder.append(param.getName());
			builder.append(DOT);
		}
		builder.append(')');
		
		return builder.toString();
	}

	public String getInternalRepresentation() {
		return internalRepresentation;
	}

	public Method getMethod() {
		return method;
	}

	public void setMethod(Method method) {
		this.method = method;
	}

	public String getName() {
		return name;
	}

	public Class getContainer() {
		return container;
	}

	public Class[] getActualParameters() {
		return actualParameters;
	}

	@Override
	public boolean equals(Object obj) {
		if (obj == null || !(obj instanceof MethodDescriptor)) {
			return false;
		}
		
		return internalRepresentation.equals(((MethodDescriptor)obj).internalRepresentation);
	}

	@Override
	public int hashCode() {
		return internalRepresentation.hashCode();
	}

	@Override
	public String toString() {
		return internalRepresentation;
	}
	
	

}
