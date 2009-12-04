/**
 * Copyright (c) 2009, Barthelemy Dagenais All rights reserved.
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
 */

package py4j;

import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import javax.script.Bindings;
import javax.script.ScriptContext;
import javax.script.ScriptEngine;
import javax.script.ScriptEngineManager;

/**
 * 
 * <p>
 * Provides default implementation of a JavaGateway.
 * </p>
 * 
 * <p>
 * This class is <b>not</b> thread-safe.
 * </p>
 * 
 * @author Barthelemy Dagenais
 * 
 */
public class DefaultGateway implements Gateway {

	private ScriptEngineManager mgr = new ScriptEngineManager();
	private ScriptEngine jsEngine = mgr.getEngineByName("JavaScript");
	private Bindings bindings = jsEngine
			.getBindings(ScriptContext.ENGINE_SCOPE);
	private int idCounter = 0;
	private boolean isStarted = false;
	private final static String OBJECT_NAME_PREFIX = "o";

	private final static String ARG_NAME_PREFIX = "a";
	
	

	@SuppressWarnings("unchecked")
	@Override
	public List<String> getMethodNames(Object obj) {
		Class clazz = obj.getClass();
		Method[] methods = clazz.getMethods();
		Set<String> methodNames = new HashSet<String>();
		for (Method method : methods) {
			methodNames.add(method.getName());
		}

		return new ArrayList<String>(methodNames);
	}

	@Override
	public String getMethodNamesAsString(Object obj) {
		List<String> methodNames = getMethodNames(obj);
		StringBuilder buffer = new StringBuilder();
		for (String methodName : methodNames) {
			buffer.append(methodName);
			buffer.append(",");
		}
		return buffer.toString();
	}

	@Override
	public void shutdown() {
		isStarted = false;
		bindings.clear();
	}

	@Override
	public void startup() {
		isStarted = true;
		bindings.put(GATEWAY_OBJECT_ID, this);
	}

	@Override
	public Object getObject(String objectId) {
		return bindings.get(objectId);
	}

	public boolean isStarted() {
		return isStarted;
	}

	public void setStarted(boolean isStarted) {
		this.isStarted = isStarted;
	}

	protected String getNextObjectId() {
		return OBJECT_NAME_PREFIX + idCounter++;
	}

	protected int getCurrentObjectId() {
		return idCounter;
	}

	protected String putNewObject(Object object) {
		String id = getNextObjectId();
		bindings.put(id, object);
		return id;
	}

	protected Bindings getBindings() {
		return bindings;
	}

	@Override
	public ReturnObject invoke(String methodName, String targetObjectId,
			List<Argument> args) {
		if (args == null) {
			args = new ArrayList<Argument>();
		}
		ReturnObject returnObject = null;
		List<String> tempArgsIds = new ArrayList<String>();
		try {
			StringBuilder methodCall = new StringBuilder();
			methodCall.append(targetObjectId);
			methodCall.append(".");
			methodCall.append(methodName);
			methodCall.append(buildArgs(args, tempArgsIds));
			methodCall.append(";");
			System.out.println("Calling: " + methodCall.toString());
			Object object = jsEngine.eval(methodCall.toString());
			if (object != null) {
				if (isPrimitiveObject(object)) {
					returnObject = ReturnObject.getPrimitiveReturnObject(object);
				} else {
					String objectId = putNewObject(object);
					// TODO Handle lists, maps, etc.
					returnObject = ReturnObject.getReferenceReturnObject(objectId);
				}
			} else {
				returnObject = ReturnObject.getNullReturnObject();
			}
		} catch (Exception e) {
			throw new Py4JException(e);
		} finally {
			cleanTempArgs(tempArgsIds);
		}

		return returnObject;
	}

	protected boolean isPrimitiveObject(Object object) {
		return object instanceof Boolean || object instanceof String
				|| object instanceof Number || object instanceof Character;
	}

	private void cleanTempArgs(List<String> tempArgsIds) {
		for (String argId : tempArgsIds) {
			bindings.remove(argId);
		}
	}

	private String buildArgs(List<Argument> args, List<String> tempArgsIds) {
		StringBuilder argsString = new StringBuilder();
		argsString.append('(');
		int i = 0;
		for (Argument arg : args) {
			if (i != 0) {
				argsString.append(',');
			}

			String argumentRef = arg.getValue().toString();
			if (!arg.isReference()) {
				String tempArgId = ARG_NAME_PREFIX + i;
				bindings.put(tempArgId, arg.getValue());
				tempArgsIds.add(tempArgId);
				argumentRef = tempArgId;
			}

			argsString.append(argumentRef);
			++i;
		}
		argsString.append(')');
		return argsString.toString();
	}

}
