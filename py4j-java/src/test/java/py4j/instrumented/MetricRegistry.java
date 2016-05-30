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

}
