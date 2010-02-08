package py4j.model;

import py4j.reflection.TypeUtil;

public class HelpPageGenerator {

	public final static String PREFIX = "|";
	public final static String INDENT = "  ";
	public final static String PREFIX_INDENT = PREFIX + INDENT;
	public final static String DOUBLE_LINES = "\n" + PREFIX_INDENT + "\n";
	public final static String SEPARATOR = "------------------------------------------------------------";
	public final static String PREFIX_SEPARATOR = PREFIX + INDENT + SEPARATOR
			+ "\n";

	public final static String getHelpPage(Py4JMethod method, boolean shortName) {
		StringBuilder builder = new StringBuilder();
		builder.append("Method \"");
		builder.append(method.getName());
		builder.append("\" of class ");
		builder.append(method.getContainer());
		builder.append("\n{\n");
		builder.append(PREFIX_INDENT);
		builder.append(method.getSignature(shortName));
		builder.append("\n}");
		return builder.toString();
	}

	public final static String getHelpPage(Py4JClass clazz, boolean shortName) {
		StringBuilder builder = new StringBuilder();

		builder.append("Help on ");

		builder.append("class ");
		builder.append(TypeUtil.getName(clazz.getName(), true));
		builder.append(" in package ");
		builder.append(TypeUtil.getPackage(clazz.getName()));
		builder.append(":\n\n");
		builder.append(clazz.getSignature(shortName));
		builder.append(" {");
		builder.append(DOUBLE_LINES);
		builder.append(PREFIX_INDENT);
		builder.append("Methods defined here:");
		builder.append(DOUBLE_LINES);
		for (Py4JMethod method : clazz.getMethods()) {
			builder.append(PREFIX_INDENT);
			builder.append(method.getSignature(shortName));
			builder.append(DOUBLE_LINES);
		}

		builder.append(PREFIX_SEPARATOR);
		builder.append(PREFIX_INDENT);
		builder.append("Fields defined here:");
		builder.append(DOUBLE_LINES);
		for (Py4JField field : clazz.getFields()) {
			builder.append(PREFIX_INDENT);
			builder.append(field.getSignature(shortName));
			builder.append(DOUBLE_LINES);
		}

		builder.append(PREFIX_SEPARATOR);
		builder.append(PREFIX_INDENT);
		builder.append("Internal classes defined here:");
		builder.append(DOUBLE_LINES);
		for (Py4JClass internalClass : clazz.getClasses()) {
			builder.append(PREFIX_INDENT);
			builder.append(internalClass.getSignature(shortName));
			builder.append(DOUBLE_LINES);
		}
		builder.append("}");
		return builder.toString();
	}

}
