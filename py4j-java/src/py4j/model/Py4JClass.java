package py4j.model;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.ArrayList;
import java.util.List;

import py4j.reflection.TypeUtil;

public class Py4JClass extends Py4JMember {

	private final String extendType;

	private final String[] implementTypes;

	private final Py4JMethod[] methods;

	private final Py4JField[] fields;

	private final Py4JClass[] classes;

	public Py4JClass(String name, String javadoc, String extendType,
			String[] implementTypes, Py4JMethod[] methods, Py4JField[] fields,
			Py4JClass[] classes) {
		super(name, javadoc);
		this.extendType = extendType;
		this.implementTypes = implementTypes;
		this.methods = methods;
		this.fields = fields;
		this.classes = classes;
	}

	public final static Py4JClass buildClass(Class<?> clazz) {
		List<Py4JClass> classes = new ArrayList<Py4JClass>();
		List<Py4JMethod> methods = new ArrayList<Py4JMethod>();
		List<Py4JField> fields = new ArrayList<Py4JField>();

		for (Class<?> memberClass : clazz.getDeclaredClasses()) {
			if (Modifier.isPublic(memberClass.getModifiers())) {
				classes.add(Py4JClass.buildClass(memberClass));
			}
		}

		for (Method method : clazz.getDeclaredMethods()) {
			if (Modifier.isPublic(method.getModifiers())) {
				methods.add(Py4JMethod.buildMethod(method));
			}
		}

		for (Field field : clazz.getDeclaredFields()) {
			if (Modifier.isPublic(field.getModifiers())) {
				fields.add(Py4JField.buildField(field));
			}
		}

		Class<?> superClass = clazz.getSuperclass();
		String extend = null;
		if (superClass != null && superClass != Object.class) {
			extend = superClass.getName();
		} 

		Class<?>[] interfaces = clazz.getInterfaces();
		String[] implementTypes = interfaces != null && interfaces.length > 0 ? TypeUtil
				.getNames(interfaces)
				: null;

		return new Py4JClass(clazz.getName(), null, extend, implementTypes,
				methods.toArray(new Py4JMethod[0]), fields
						.toArray(new Py4JField[0]), classes
						.toArray(new Py4JClass[0]));
	}

	public Py4JMethod[] getMethods() {
		return methods;
	}

	public Py4JField[] getFields() {
		return fields;
	}

	public Py4JClass[] getClasses() {
		return classes;
	}

	public String getExtendType() {
		return extendType;
	}

	public String[] getImplementTypes() {
		return implementTypes;
	}

	@Override
	public String getSignature(boolean shortName) {
		StringBuilder builder = new StringBuilder();
		
		builder.append(TypeUtil.getName(getName(), shortName));
		if (extendType != null) {
			builder.append(" extends ");
			builder.append(extendType);
		}
		
		if (implementTypes != null) {
			builder.append(" implements ");
			int length = implementTypes.length;
			for (int i = 0; i<length-1; i++) {
				builder.append(implementTypes[i]);
				builder.append(", ");
			}
			builder.append(implementTypes[length-1]);
		}
		return builder.toString();
	}
}
