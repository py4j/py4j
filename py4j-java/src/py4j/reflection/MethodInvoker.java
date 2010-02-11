/*******************************************************************************
 * Copyright (c) 2010, Barthelemy Dagenais All rights reserved.
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

import java.lang.reflect.Constructor;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

import py4j.Py4JException;

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

	private int cost;

	private TypeConverter[] converters;

	private Method method;

	private Constructor<?> constructor;

	private final Logger logger = Logger.getLogger(MethodInvoker.class
			.getName());

	public static final MethodInvoker INVALID_INVOKER = new MethodInvoker(
			(Method) null, null, INVALID_INVOKER_COST);

	public MethodInvoker(Method method, TypeConverter[] converters, int cost) {
		super();
		this.method = method;
		this.converters = converters;
		this.cost = cost;
	}

	public MethodInvoker(Constructor<?> constructor,
			TypeConverter[] converters, int cost) {
		super();
		this.constructor = constructor;
		this.converters = converters;
		this.cost = cost;
	}

	public int getCost() {
		return cost;
	}

	public Method getMethod() {
		return method;
	}

	public Constructor<?> getConstructor() {
		return constructor;
	}

	public Object invoke(Object obj, Object[] arguments) {
		Object returnObject = null;

		try {
			Object[] newArguments = arguments;

			if (converters != null) {
				int size = arguments.length;
				newArguments = new Object[size];
				for (int i = 0; i < size; i++) {
					newArguments[i] = converters[i].convert(arguments[i]);
				}
			}
			if (method != null) {
				method.setAccessible(true);
				returnObject = method.invoke(obj, newArguments);
			} else if (constructor != null) {
				constructor.setAccessible(true);
				returnObject = constructor.newInstance(newArguments);
			}
		} catch (Exception e) {
			logger
					.log(
							Level.WARNING,
							"Could not invoke method or received an exception while invoking.",
							e);
			throw new Py4JException(e);
		}

		return returnObject;
	}

	public boolean isVoid() {
		if (constructor != null) {
			return false;
		} else {
			return method.getReturnType().equals(void.class);
		}
	}

	public TypeConverter[] getConverters() {
		return converters;
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
			cost = buildConverters(converters, constructor.getParameterTypes(),
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
			cost = buildConverters(converters, method.getParameterTypes(),
					arguments);
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

	private static int buildConverters(List<TypeConverter> converters,
			Class<?>[] parameters, Class<?>[] arguments) {
		int cost = 0;
		int tempCost = -1;
		int size = arguments.length;
		for (int i = 0; i < size; i++) {
			if (parameters[i].isAssignableFrom(arguments[i])) {
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

}
