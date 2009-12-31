package py4j.reflection;

import java.util.HashSet;
import java.util.Set;

public class TypeUtil {
	private static Set<String> numericTypes;
	
	static {
		numericTypes = new HashSet<String>();
		numericTypes.add(long.class.getName());
		numericTypes.add(int.class.getName());
		numericTypes.add(short.class.getName());
		numericTypes.add(byte.class.getName());
		numericTypes.add(double.class.getName());
		numericTypes.add(float.class.getName());
		numericTypes.add(Long.class.getName());
		numericTypes.add(Integer.class.getName());
		numericTypes.add(Short.class.getName());
		numericTypes.add(Byte.class.getName());
		numericTypes.add(Double.class.getName());
		numericTypes.add(Float.class.getName());
	}
	
	public static boolean isNumeric(Class<?> clazz) {
		return numericTypes.contains(clazz.getName()) ;
	}

	public static boolean isCharacter(Class<?> clazz) {
		return clazz.equals(Character.class) || clazz.equals(char.class);
	}

	public static boolean isBoolean(Class<?> clazz) {
		return clazz.equals(Boolean.class) || clazz.equals(boolean.class);
	}
}
