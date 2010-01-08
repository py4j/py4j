/*******************************************************************************
 * Copyright (c) 2009, 2010, Barthelemy Dagenais All rights reserved.
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

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

import py4j.Py4JException;

public class ReflectionEngine {

	public static int cacheSize = 100;

	private final Logger logger = Logger.getLogger(ReflectionEngine.class
			.getName());

	public final static Object RETURN_VOID = new Object();

	public Field getField(Class<?> clazz, String name) {
		Field field = null;

		try {
			field = clazz.getField(name);
			if (!Modifier.isPublic(field.getModifiers())
					&& !field.isAccessible()) {
				field = null;
			}
		} catch (NoSuchFieldException e) {
			field = null;
		} catch (Exception e) {
			field = null;
		}

		return field;
	}

	public Field getField(Object obj, String name) {
		return getField(obj.getClass(), name);
	}

	public Field getField(String classFQN, String name) {
		Class<?> clazz = null;

		try {
			clazz = Class.forName(classFQN);
		} catch (Exception e) {
			logger.log(Level.WARNING, "Class FQN does not exist: " + classFQN,
					e);
			throw new Py4JException(e);
		}

		return getField(clazz, name);

	}

	public Object getFieldValue(Object obj, Field field) {
		Object fieldValue = null;

		try {
			fieldValue = field.get(obj);
		} catch (Exception e) {
			logger.log(Level.SEVERE, "Error while fetching field value of "
					+ field, e);
			throw new Py4JException(e);
		}
		return fieldValue;
	}

	public MethodInvoker getMethod(Class<?> clazz, String name,
			Class<?>[] parameters) {
		MethodDescriptor mDescriptor = new MethodDescriptor(name, clazz,
				parameters);
		MethodInvoker mInvoker = null;
		List<Method> acceptableMethods = null;
		LRUCache<MethodDescriptor, MethodInvoker> cache = cacheHolder.get();

		mInvoker = cache.get(mDescriptor);

		if (mInvoker == null) {
			acceptableMethods = getMethodsByNameAndLength(clazz, name,
					parameters.length);

			if (acceptableMethods.size() == 1) {
				mInvoker = MethodInvoker.buildInvoker(acceptableMethods.get(0),
						parameters);
			} else {
				mInvoker = getBestMethod(acceptableMethods, parameters);
			}

			if (mInvoker != null && mInvoker.getCost() != -1) {
				cache.put(mDescriptor, mInvoker);
			} else {
				String errorMessage = "Method " + name + "("
						+ Arrays.toString(parameters) + ") does not exist";
				logger.log(Level.WARNING, errorMessage);
				throw new Py4JException(errorMessage);
			}
		}

		return mInvoker;
	}

	private MethodInvoker getBestMethod(List<Method> acceptableMethods,
			Class<?>[] parameters) {
		MethodInvoker lowestCost = null;

		for (Method method : acceptableMethods) {
			MethodInvoker temp = MethodInvoker.buildInvoker(method, parameters);
			int cost = temp.getCost();
			if (cost == -1) {
				continue;
			} else if (cost == 0) {
				lowestCost = temp;
				break;
			} else if (lowestCost == null || cost < lowestCost.getCost()) {
				lowestCost = temp;
			}
		}

		return lowestCost;
	}

	private List<Method> getMethodsByNameAndLength(Class<?> clazz, String name,
			int length) {
		List<Method> methods = new ArrayList<Method>();

		for (Method method : clazz.getMethods()) {
			if (method.getName().equals(name)
					&& method.getParameterTypes().length == length) {
				methods.add(method);
			}
		}

		return methods;
	}

	public MethodInvoker getMethod(String classFQN, String name,
			Object[] parameters) {
		Class<?> clazz = null;

		try {
			clazz = Class.forName(classFQN);
		} catch (Exception e) {
			logger.log(Level.WARNING, "Class FQN does not exist: " + classFQN,
					e);
			throw new Py4JException(e);
		}

		return getMethod(clazz, name, getClassParameters(parameters));
	}

	public MethodInvoker getMethod(Object object, String name,
			Object[] parameters) {
		return getMethod(object.getClass(), name,
				getClassParameters(parameters));
	}

	private Class<?>[] getClassParameters(Object[] parameters) {
		int size = parameters.length;
		Class<?>[] classes = new Class<?>[size];

		for (int i = 0; i < size; i++) {
			classes[i] = parameters[i].getClass();
		}

		return classes;
	}

	public Object invokeMethod(Object object, MethodInvoker invoker,
			Object[] parameters) {
		Object returnObject = null;

		returnObject = invoker.invoke(object, parameters);
		if (invoker.isVoid()) {
			returnObject = RETURN_VOID;
		}

		return returnObject;
	}

	private static ThreadLocal<LRUCache<MethodDescriptor, MethodInvoker>> cacheHolder = new ThreadLocal<LRUCache<MethodDescriptor, MethodInvoker>>() {

		@Override
		protected LRUCache<MethodDescriptor, MethodInvoker> initialValue() {
			return new LRUCache<MethodDescriptor, MethodInvoker>(cacheSize);
		}

	};
}
