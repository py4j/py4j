package py4j.reflection;

import java.util.Collection;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class LRUCache<K,V> implements Map<K, V> {

	private Map<K, V> internalMap;
	
	private List<K> lruList;
	
	private final int cacheSize;
	
	public LRUCache(int cacheSize) {
		this.cacheSize = cacheSize;
		this.lruList = new LinkedList<K>();
		this.internalMap = new HashMap<K, V>();
	}

	@Override
	public void clear() {
		internalMap.clear();
		lruList.clear();
		
	}

	@Override
	public boolean containsKey(Object key) {
		return internalMap.containsKey(key);
	}

	@Override
	public boolean containsValue(Object value) {
		return internalMap.containsValue(value);
	}

	@Override
	public Set<java.util.Map.Entry<K, V>> entrySet() {
		return internalMap.entrySet();
	}

	@SuppressWarnings("unchecked")
	@Override
	public V get(Object key) {
		boolean found = lruList.remove(key);
		if (found) {
			lruList.add(0, (K)key);
		}
		return internalMap.get(key);
	}

	@Override
	public boolean isEmpty() {
		return internalMap.isEmpty();
	}

	@Override
	public Set<K> keySet() {
		return internalMap.keySet();
	}

	@Override
	public V put(K key, V value) {
		lruList.remove(key);
		if (lruList.size() >= cacheSize) {
			K oldKey = lruList.remove(cacheSize-1);
			internalMap.remove(oldKey);
		}
		
		lruList.add(0, key);
		return internalMap.put(key, value);
	}

	@Override
	public void putAll(Map<? extends K, ? extends V> map) {
		for (K newKey : map.keySet()) {
			internalMap.put(newKey, map.get(newKey));
		}
	}

	@Override
	public V remove(Object key) {
		lruList.remove(key);
		return internalMap.remove(key);
	}

	@Override
	public int size() {
		return internalMap.size();
	}

	@Override
	public Collection<V> values() {
		return internalMap.values();
	}

	// For testing purpose
	protected List<K> getLRUList() {
		return lruList;
	}
	
	// For testing purpose
	protected  Map<K,V> getInternalMap() {
		return internalMap;
	}
	
}
