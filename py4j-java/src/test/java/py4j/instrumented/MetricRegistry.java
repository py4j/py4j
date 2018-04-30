/******************************************************************************
 * Copyright (c) 2009-2018, Barthelemy Dagenais and individual contributors.
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
package py4j.instrumented;

import java.util.Collections;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

public class MetricRegistry {

	private final static ConcurrentMap<String, String> createdObjects = new ConcurrentHashMap<String, String>();

	private final static ConcurrentMap<String, String> finalizedObjects = new ConcurrentHashMap<String, String>();

	public static void addCreatedObject(Object obj) {
		String str = obj.toString();
		createdObjects.put(str, str);
	}

	public static void addFinalizedObject(Object obj) {
		String str = obj.toString();
		finalizedObjects.put(str, str);
	}

	public static Set<String> getCreatedObjectsKeySet() {
		return Collections.unmodifiableSet(createdObjects.keySet());
	}

	public static Set<String> getFinalizedObjectsKeySet() {
		return Collections.unmodifiableSet(finalizedObjects.keySet());
	}

	public static void forceFinalization() {
		// Try to call System.gc() and System.runFinalizers()
		// Multiple times to increase likelihood of finalization.
		for (int i = 0; i < 10; i++) {
			System.gc();
			System.runFinalization();
		}
	}

	public static void sleep() {
		try {
			Thread.currentThread().sleep(2000);
		} catch (Exception e) {

		}
	}

}
