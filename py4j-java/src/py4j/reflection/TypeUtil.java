package py4j.reflection;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
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

	public static boolean isInteger(Class<?> clazz) {
		return clazz.equals(Integer.class) || clazz.equals(int.class);
	}

	public static boolean isLong(Class<?> clazz) {
		return clazz.equals(Long.class) || clazz.equals(long.class);
	}

	public static boolean isDouble(Class<?> clazz) {
		return clazz.equals(Double.class) || clazz.equals(double.class);
	}

	public static boolean isFloat(Class<?> clazz) {
		return clazz.equals(Float.class) || clazz.equals(float.class);
	}

	public static boolean isShort(Class<?> clazz) {
		return clazz.equals(Short.class) || clazz.equals(short.class);
	}

	public static boolean isByte(Class<?> clazz) {
		return clazz.equals(Byte.class) || clazz.equals(byte.class);
	}

	public static boolean isNumeric(Class<?> clazz) {
		return numericTypes.contains(clazz.getName());
	}

	public static boolean isCharacter(Class<?> clazz) {
		return clazz.equals(Character.class) || clazz.equals(char.class);
	}

	public static boolean isBoolean(Class<?> clazz) {
		return clazz.equals(Boolean.class) || clazz.equals(boolean.class);
	}

	public static int getPoint(Class<?> clazz) {
		int point = -1;
		if (isByte(clazz)) {
			point = 0;
		} else if (isShort(clazz)) {
			point = 1;
		} else if (isInteger(clazz)) {
			point = 2;
		} else if (isLong(clazz)) {
			point = 3;
		}
		return point;
	}

	public static int getCost(Class<?> parent, Class<?> child) {
		return getPoint(parent) - getPoint(child);
	}

	public static int computeDistance(Class<?> parent, Class<?> child) {
		int distance = -1;
		if (parent.equals(child)) {
			distance = 0;
		}

		// Search through super classes
		if (distance == -1) {
			distance = computeSuperDistance(parent, child);
		}

		// Search through interfaces (costly)
		if (distance == -1) {
			distance = computeInterfaceDistance(parent, child,
					new HashSet<String>(), Arrays.asList(child.getInterfaces()));
		}

		return distance;
	}

	private static int computeSuperDistance(Class<?> parent, Class<?> child) {
		Class<?> superChild = child.getSuperclass();
		if (superChild == null) {
			return -1;
		} else if (superChild.equals(parent)) {
			return 1;
		} else {
			int distance = computeSuperDistance(parent, superChild);
			if (distance != -1) {
				return distance + 1;
			} else {
				return distance;
			}
		}
	}

	private static int computeInterfaceDistance(Class<?> parent,
			Class<?> child, Set<String> visitedInterfaces,
			List<Class<?>> interfacesToVisit) {
		int distance = -1;
		List<Class<?>> nextInterfaces = new ArrayList<Class<?>>();
		for (Class<?> clazz : interfacesToVisit) {
			if (parent.equals(clazz)) {
				distance = 1;
				break;
			} else {
				visitedInterfaces.add(clazz.getName());
				getNextInterfaces(clazz, nextInterfaces, visitedInterfaces);
			}
		}

		if (distance == -1) {
			if (child != null) {
				getNextInterfaces(child.getSuperclass(), nextInterfaces,
						visitedInterfaces);
				int newDistance = computeInterfaceDistance(parent, child
						.getSuperclass(), visitedInterfaces, nextInterfaces);
				if (newDistance != -1) {
					distance = newDistance + 1;
				}
			}
		}

		return distance;
	}

	private static void getNextInterfaces(Class<?> clazz,
			List<Class<?>> nextInterfaces, Set<String> visitedInterfaces) {
		if (clazz != null) {
			for (Class<?> nextClazz : clazz.getInterfaces()) {
				if (!visitedInterfaces.contains(nextClazz.getName())) {
					nextInterfaces.add(nextClazz);
				}
			}
		}
	}

	public static int computeNumericConversion(Class<?> parent, Class<?> child,
			List<TypeConverter> converters) {
		int cost = -1;

		// XXX This is not complete. Certain cases are not considered like from
		// Long to Int, Long to short, and the like. This is not a problem for
		// Py4J. This could be a problem for pure Java. But type conversion is
		// NOT required for pure Java, only for scripting languages with less
		// primitives.

		if (isLong(parent) && (!isFloat(child) && !isDouble(child))) {
			cost = getCost(parent, child);
			converters.add(TypeConverter.NO_CONVERTER);
		} else if (isInteger(parent)
				&& (isInteger(child) || isShort(child) || isByte(child))) {
			cost = getCost(parent, child);
			converters.add(TypeConverter.NO_CONVERTER);
		} else if (isShort(parent)) {
			if (isShort(child) || isByte(child)) {
				cost = getCost(parent, child);
				converters.add(TypeConverter.NO_CONVERTER);
			} else if (isInteger(child)) {
				cost = 1;
				converters.add(TypeConverter.SHORT_CONVERTER);
			}
		} else if (isByte(parent)) {
			if (isByte(child)) {
				cost = 0;
				converters.add(TypeConverter.NO_CONVERTER);
			} else if (isInteger(child)) {
				cost = 2;
				converters.add(TypeConverter.BYTE_CONVERTER);
			}
		} else if (isDouble(parent)) {
			if (isDouble(child)) {
				cost = 0;
				converters.add(TypeConverter.NO_CONVERTER);
			} else if (isFloat(child)) {
				cost = 1;
				converters.add(TypeConverter.NO_CONVERTER);
			}
		} else if (isFloat(parent)) {
			if (isFloat(child)) {
				cost = 0;
				converters.add(TypeConverter.NO_CONVERTER);
			} else if (isDouble(child)) {
				cost = 1;
				converters.add(TypeConverter.FLOAT_CONVERTER);
			}
		}

		return cost;
	}

	public static int computeCharacterConversion(Class<?> parent,
			Class<?> child, List<TypeConverter> converters) {
		int cost = -1;

		if (isCharacter(child)) {
			cost = 0;
			converters.add(TypeConverter.NO_CONVERTER);
		} else if (CharSequence.class.isAssignableFrom(child)) {
			cost = 1;
			converters.add(TypeConverter.CHAR_CONVERTER);
		}

		return cost;
	}
}
