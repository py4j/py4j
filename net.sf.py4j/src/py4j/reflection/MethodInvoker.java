/*******************************************************************************
 * Copyright (c) 2010, 2011, Barthelemy Dagenais All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * - Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
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
 *******************************************************************************/
package py4j.reflection;

import java.lang.reflect.AccessibleObject;
import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Arrays;
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

	private static int buildConverters(List<TypeConverter> converters,
			                           AccessibleObject exec, Class<?>[] arguments) {
		
		Class<?>[] parameters = getParameterTypes(exec);
		int cost = 0;
		int tempCost = -1;
		int size = arguments.length;
		for (int i = 0; i < size; i++) {
			if (arguments[i] == null) {
				if (parameters[i].isPrimitive()) {
					tempCost = -1;
				} else {
					int distance = TypeUtil.computeDistance(new Object().getClass(), parameters[i]);
					tempCost = Math.abs(MAX_DISTANCE - distance);
					converters.add(TypeConverter.NO_CONVERTER);
				}
			} else if (parameters[i].isAssignableFrom(arguments[i])) {
				tempCost = TypeUtil
						.computeDistance(parameters[i], arguments[i]);
				converters.add(TypeConverter.NO_CONVERTER);
			} else if (TypeUtil.isNumeric(parameters[i])
					&& TypeUtil.isNumeric(arguments[i])) {
				tempCost = TypeUtil.computeNumericConversion(parameters[i],
						arguments[i], converters);
			} else if (TypeUtil.isCharacter(parameters[i])) {
				tempCost = TypeUtil.computeCharacterConversion(parameters[i],
						arguments[i], converters);
			} else if (TypeUtil.isBoolean(parameters[i])
					&& TypeUtil.isBoolean(arguments[i])) {
				tempCost = 0;
				converters.add(TypeConverter.NO_CONVERTER);
				
			// Deal with converting enums
			} else if (parameters[i].isEnum() && arguments[i].isAssignableFrom(String.class)) {
				tempCost = 0;
				converters.add(new TypeConverter((Class<Enum>)parameters[i]));
			
			// Deal with varargs if we are 
			} else if (isVarArgs(exec) && i == parameters.length-1) { // If we are the last argument and varargs, it can be an array
				// Maybe the rest of the arguments are varargs?
				Class arrayClass = parameters[i].getComponentType();
				boolean varArgsOk = false;
				for (int j = i; j<arguments.length;++j) {
					if (arrayClass.isAssignableFrom(arguments[j])) {
						varArgsOk = true;
						continue;
					}
					varArgsOk = false;
					break;
				}

				if (varArgsOk) {
					tempCost = 0;
					converters.add(TypeConverter.VARARGS_CONVERTER);
					break;
				}
			}

			if (tempCost != -1) {
				cost += tempCost;
				tempCost = -1;
			} else {
				cost = -1;
				break;
			}
		}
		return cost;
	}

	private static boolean isVarArgs(AccessibleObject exec) {
		return exec instanceof Method ? ((Method)exec).isVarArgs() : ((Constructor)exec).isVarArgs();
	}

	private static Class<?>[] getParameterTypes(AccessibleObject exec) {
		return exec instanceof Method ? ((Method)exec).getParameterTypes() : ((Constructor)exec).getParameterTypes();
	}

	public static MethodInvoker buildInvoker(Constructor<?> constructor,
			Class<?>[] arguments) {
		MethodInvoker invoker = null;
		int size = arguments.length;
		int cost = 0;

		List<TypeConverter> converters = new ArrayList<TypeConverter>();
		if (arguments == null || size == 0) {
			invoker = new MethodInvoker(constructor, null, 0);
		} else {
			cost = buildConverters(converters, constructor,
					arguments);
		}
		if (cost == -1) {
			invoker = INVALID_INVOKER;
		} else {
			TypeConverter[] convertersArray = null;
			if (!allNoConverter(converters)) {
				convertersArray = converters.toArray(new TypeConverter[0]);
			}
			invoker = new MethodInvoker(constructor, convertersArray, cost);
		}

		return invoker;
	}

	public static MethodInvoker buildInvoker(Method method, Class<?>[] arguments) {
		MethodInvoker invoker = null;
		int size = arguments.length;
		int cost = 0;

		List<TypeConverter> converters = new ArrayList<TypeConverter>();
		if (arguments == null || size == 0) {
			invoker = new MethodInvoker(method, null, 0);
		} else {
			cost = buildConverters(converters, method, arguments);
		}
		if (cost == -1) {
			invoker = INVALID_INVOKER;
		} else {
			TypeConverter[] convertersArray = null;
			if (!allNoConverter(converters)) {
				convertersArray = converters.toArray(new TypeConverter[0]);
			}
			invoker = new MethodInvoker(method, convertersArray, cost);
		}

		return invoker;
	}

	private int cost;

	private TypeConverter[] converters;

	private AccessibleObject executable;

	private final Logger logger = Logger.getLogger(MethodInvoker.class
			.getName());

	public static final MethodInvoker INVALID_INVOKER = new MethodInvoker(
			(Method) null, null, INVALID_INVOKER_COST);

	public MethodInvoker(Constructor<?> constructor,
			TypeConverter[] converters, int cost) {
		super();
		this.executable = constructor;
		this.converters = converters;
		this.cost = cost;
	}

	public MethodInvoker(Method method, TypeConverter[] converters, int cost) {
		super();
		this.executable = method;
		this.converters = converters;
		this.cost = cost;
	}

	public TypeConverter[] getConverters() {
		return converters;
	}

	public int getCost() {
		return cost;
	}

	public Object invoke(Object obj, Object[] arguments) {
		
		Object returnObject = null;
		try {
			Object[] newArguments = arguments;

			if (converters != null) {
				int size = arguments.length;
				newArguments = Arrays.copyOf(newArguments, newArguments.length);
				for (int i = 0; i < size; i++) {
					// For VarArgs method where this is the last converter
					// transform all remaining arguments
					if( i == getParameterCount(executable)-1 && converters[i].isVarArgs()) { // last converter
						newArguments = converters[i].convert(i, newArguments);
						break;
					} else {
					    newArguments[i] = converters[i].convert(arguments[i]);
					}
				}
			}
			
			executable.setAccessible(true);
			if (executable instanceof Method) {
				returnObject = ((Method)executable).invoke(obj, newArguments);
			} else if (executable instanceof Constructor) {
				returnObject = ((Constructor)executable).newInstance(newArguments);
			}
		} catch (InvocationTargetException ie) {
			logger.log(Level.WARNING, "Exception occurred in client code.", ie);
			throw new Py4JJavaException(ie.getCause());
		} catch (Exception e) {
			logger.log(
					Level.WARNING,
					"Could not invoke method or received an exception while invoking.",
					e);
			throw new Py4JException(e);
		}

		return returnObject;
	}

	private int getParameterCount(AccessibleObject exec) {
		return exec instanceof Method ? ((Method)exec).getParameterTypes().length : ((Constructor)exec).getParameterCount();
	}

	public boolean isVoid() {
		if (executable instanceof Constructor) {
			return false;
		} else {
			return ((Method)executable).getReturnType().equals(void.class);
		}
	}

}
