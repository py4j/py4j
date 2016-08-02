/******************************************************************************
 * Copyright (c) 2009-2016, Barthelemy Dagenais and individual contributors.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * - Redistributions of source code must retain the above copyright notice,
 * this list of conditions and the following disclaimer.
 *
 * - Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 *
 * - The name of the author may not be used to endorse or promote products
 * derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 *****************************************************************************/
package py4j.reflection;

import java.lang.reflect.AccessibleObject;
import java.lang.reflect.Array;
import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.security.AccessController;
import java.security.PrivilegedAction;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

import py4j.Py4JException;
import py4j.Py4JJavaException;

/**
 * <p>
 * A MethodInvoker translates a call made in a Python Program into a call to a
 * Java method.
 * </p>
 * <p>
 * A MethodInvoker is tailored to a particular set of actual parameters and
 * indicates how far the calling context is from the method signature.
 * </p>
 * <p>
 * For example, a call to method1(String) from Python can be translated to a
 * call to method1(char) in Java, with a cost of 1.
 * </p>
 * 
 * @author Barthelemy Dagenais
 * 
 */
public class MethodInvoker {

	public final static int INVALID_INVOKER_COST = -1;

	public final static int MAX_DISTANCE = 100000000;

	private static boolean allNoConverter(List<TypeConverter> converters) {
		boolean allNo = true;

		for (TypeConverter converter : converters) {
			if (converter != TypeConverter.NO_CONVERTER) {
				allNo = false;
				break;
			}
		}

		return allNo;
	}

	private static int buildConverters(List<TypeConverter> converters, AccessibleObject accessible, Class<?>[] arguments) {
		int cost = 0;
		int tempCost = -1;
		int size = arguments.length;
		Class<?>[] parameters = getParameterTypes(accessible);
		boolean isVarArgs = isVarArgs(accessible);
		for (int i = 0; i < size; i++) {
			Class<?> iClass = arguments[i]; // input or given class
			Class<?> rClass = parameters[i]; // required or specified type

			tempCost = convertArgument(converters, iClass, rClass);

			if (tempCost == -1 &&  isVarArgs && i == parameters.length - 1) { // If we are the last argument and varargs, it can be an array
				Class<?> arrayClass = rClass.getComponentType();
				boolean varArgsOk = true;
				List<TypeConverter> arrayConverters = new ArrayList<TypeConverter>();
				for (int j = i; j < size; ++j) {
					tempCost = convertArgument(arrayConverters, arrayClass, arguments[j]);
					if (tempCost == -1) {
						varArgsOk = false;
						break;
					}
				}
				tempCost = -1;
				if (varArgsOk) {
					converters.add(TypeConverter.VARARGS_CONVERTER);
					break;
				}
			}

			if (tempCost == -1) { // could not convert
				cost = -1;
				break;
			}
			cost += tempCost;
			tempCost = -1;
		}

		if (cost == 0 && (parameters.length > size || isVarArgs)) {
			cost += 1;
		}
		return cost;
	}

	private static int convertArgument(List<TypeConverter> converters, Class<?> iClass, Class<?> rClass) {
		int tempCost = -1;
		if (iClass == null) {
			if (rClass.isPrimitive()) {
				tempCost = -1;
			} else {
				int distance = TypeUtil.computeDistance(Object.class, rClass);
				tempCost = Math.abs(MAX_DISTANCE - distance);
				converters.add(TypeConverter.NO_CONVERTER);
			}
		} else if (rClass.isAssignableFrom(iClass)) {
			tempCost = TypeUtil.computeDistance(rClass, iClass);
			converters.add(TypeConverter.NO_CONVERTER);
		} else if (TypeUtil.isNumeric(rClass) && TypeUtil.isNumeric(iClass)) {
			tempCost = TypeUtil.computeNumericConversion(rClass, iClass, converters);
		} else if (TypeUtil.isCharacter(rClass)) {
			tempCost = TypeUtil.computeCharacterConversion(rClass, iClass, converters);
		} else if (TypeUtil.isBoolean(rClass) && TypeUtil.isBoolean(iClass)) {
			tempCost = 0;
			converters.add(TypeConverter.NO_CONVERTER);
		}

		return tempCost;
	}

	/**
	 * @param accessible Must be a Constructor or Method
	 * @param arguments classes of given arguments (note primitives are boxed)
	 * @return
	 */
	public static MethodInvoker buildInvoker(AccessibleObject accessible, Class<?>... arguments) {
		if (!(accessible instanceof Constructor || accessible instanceof Method)) {
			throw new IllegalArgumentException("AccessibleObject must be a Constructor or Method");
		}

		MethodInvoker invoker = null;
		int size = arguments == null ? 0 : arguments.length;
		int cost = 0;

		List<TypeConverter> converters = new ArrayList<TypeConverter>();
		if (size > 0) {
			cost = buildConverters(converters, accessible, arguments);
		} else if (isVarArgs(accessible)) {
			cost++; // increase cost to bias null invocations
		}
		if (cost == -1) {
			invoker = INVALID_INVOKER;
		} else {
			TypeConverter[] convertersArray = null;
			if (!allNoConverter(converters)) {
				convertersArray = converters.toArray(new TypeConverter[0]);
			}
			invoker = new MethodInvoker(accessible, convertersArray, cost);
		}

		return invoker;
	}


	private int cost;

	private List<TypeConverter> converters;

	private AccessibleObject accessible;

	private final Logger logger = Logger.getLogger(MethodInvoker.class.getName());

	public static final MethodInvoker INVALID_INVOKER = new MethodInvoker(null, null, INVALID_INVOKER_COST);

	public MethodInvoker(AccessibleObject accessible, TypeConverter[] converters, int cost) {
		super();
		if (!(accessible == null || accessible instanceof Constructor || accessible instanceof Method)) {
			throw new IllegalArgumentException("AccessibleObject must be a Constructor, Method or null");
		}
		this.accessible = accessible;
		if (converters != null) {
			this.converters = Collections.unmodifiableList(Arrays.asList(converters));
		}
		this.cost = cost;
	}

	public Constructor<?> getConstructor() {
		return (Constructor<?>) (accessible instanceof Constructor ? accessible : null);
	}

	public List<TypeConverter> getConverters() {
		return converters;
	}

	/**
	 * @return some metric for determining the amount of conversion needed (negative means cannot convert)
	 */
	public int getCost() {
		return cost;
	}

	public Method getMethod() {
		return (Method) (accessible instanceof Method ? accessible : null);
	}

	public Object invoke(Object obj, Object... arguments) {
		Object returnObject = null;

		try {
			int size = arguments == null ? 0 : arguments.length;
			int count = getParameterCount(accessible);
			Object[] newArguments = arguments;

			if (converters != null) {
				newArguments = Arrays.copyOf(newArguments, size);
				for (int i = 0; i < size; i++) {
					TypeConverter converter = converters.get(i);
					if (i == count - 1 && converter.isVarArgs()) {
						newArguments = converter.convert(getParameterTypes(accessible)[i].getComponentType(), i, newArguments);
						break;
					} else {
						newArguments[i] = converter.convert(arguments[i]);
					}
				}
			} else if (size == 0 && isVarArgs(accessible)) {
				newArguments = new Object[] {null};
			} else if (size == count - 1) {
				if (isVarArgs(accessible)) { // pad with empty array
					newArguments = Arrays.copyOf(newArguments, count);
					newArguments[size] = Array.newInstance(getParameterTypes(accessible)[size].getComponentType(), 0);
				}
			}
			if (accessible != null) {
				AccessController.doPrivileged(new PrivilegedAction<Object>() {
					public Object run() {
						accessible.setAccessible(true);
						return null;
					}
				});
				if (accessible instanceof Method) {
					returnObject = ((Method) accessible).invoke(obj, newArguments);
				} else if (accessible instanceof Constructor) {
					returnObject = ((Constructor<?>) accessible).newInstance(newArguments);
				}
			}
		} catch (InvocationTargetException ie) {
			logger.log(Level.WARNING, "Exception occurred in client code.", ie);
			throw new Py4JJavaException(ie.getCause());
		} catch (Exception e) {
			logger.log(Level.WARNING, "Could not invoke method or received an exception while invoking.", e);
			throw new Py4JException(e);
		}

		return returnObject;
	}

	@SuppressWarnings("rawtypes")
	private static boolean isVarArgs(AccessibleObject accessible) {
		return accessible == null ? false : accessible instanceof Method ? ((Method) accessible).isVarArgs() : ((Constructor) accessible).isVarArgs();
	}

	@SuppressWarnings("rawtypes")
	private static Class<?>[] getParameterTypes(AccessibleObject accessible) {
		return accessible == null ? null : accessible instanceof Method ? ((Method) accessible).getParameterTypes() : ((Constructor) accessible).getParameterTypes();
	}

	@SuppressWarnings("rawtypes")
	private static int getParameterCount(AccessibleObject accessible) {
		return accessible == null ? 0 : accessible instanceof Method ? ((Method) accessible).getParameterCount() : ((Constructor) accessible).getParameterCount();
	}

	public boolean isVoid() {
		if (accessible instanceof Constructor) {
			return false;
		} else if (accessible instanceof Method) {
			return ((Method) accessible).getReturnType().equals(void.class);
		} else {
			throw new Py4JException("Null method or constructor");
		}
	}
}
