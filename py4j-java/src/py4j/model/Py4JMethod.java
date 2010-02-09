package py4j.model;

import java.lang.reflect.Method;

import py4j.reflection.TypeUtil;

public class Py4JMethod extends Py4JMember {

	private final String[] parameterTypes;

	// Currently not supported.
	private final String[] parameterNames;

	private final String returnType;

	private final String container;

	public Py4JMethod(String name, String javadoc, String[] parameterTypes,
			String[] parameterNames, String returnType, String container) {
		super(name, javadoc);
		this.parameterTypes = parameterTypes;
		this.parameterNames = parameterNames;
		this.returnType = returnType;
		this.container = container;
	}

	public final static Py4JMethod buildMethod(Method method) {
		return new Py4JMethod(method.getName(), null, TypeUtil.getNames(method
				.getParameterTypes()), null, method.getReturnType().getCanonicalName(), method.getDeclaringClass().getCanonicalName());
	}
	
	public String[] getParameterTypes() {
		return parameterTypes;
	}

	public String[] getParameterNames() {
		return parameterNames;
	}

	public String getReturnType() {
		return returnType;
	}

	public String getContainer() {
		return container;
	}

	@Override
	public String getSignature(boolean shortName) {
		StringBuilder builder = new StringBuilder();
		int length = parameterTypes.length;
		builder.append(getName());
		builder.append('(');
		for (int i = 0; i < length - 1; i++) {
			builder.append(TypeUtil.getName(parameterTypes[i], shortName));
			builder.append(", ");
		}
		if (length > 0) {
			builder.append(TypeUtil.getName(parameterTypes[length - 1],
					shortName));
		}
		builder.append(") : ");
		builder.append(TypeUtil.getName(returnType, shortName));

		return builder.toString();
	}

}
