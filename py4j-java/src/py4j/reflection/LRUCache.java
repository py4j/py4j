package py4j.reflection;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Set;

public class LRUCache<K> implements Set<K> {

	private List<K> lruList;

	private final int cacheSize;

	public LRUCache(int cacheSize) {
		this.cacheSize = cacheSize;
		this.lruList = new LinkedList<K>();
	}

	@Override
	public void clear() {
		lruList.clear();

	}

	@Override
	public boolean contains(Object key) {
		return lruList.contains(key);
	}

	public K get(Object key) {
		int index = lruList.indexOf(key);
		K newKey = null;
		if (index >= 0) {
			newKey = lruList.remove(index);
			lruList.add(0, (K) newKey);
		}
		return newKey;
	}

	@Override
	public boolean isEmpty() {
		return lruList.isEmpty();
	}

	@Override
	public boolean remove(Object key) {
		return lruList.remove(key);
	}

	// For testing purpose
	protected List<K> getLRUList() {
		return lruList;
	}

	@Override
	public boolean add(K key) {
		boolean found = lruList.remove(key);
		if (lruList.size() >= cacheSize) {
			lruList.remove(cacheSize - 1);
		}

		lruList.add(0, key);

		return !found;
	}

	@Override
	public boolean addAll(Collection<? extends K> collection) {
		boolean changed = false;

		for (K element : collection) {
			changed = add(element) || changed;
		}
		return changed;
	}

	@Override
	public boolean containsAll(Collection<?> collection) {
		boolean contains = true;

		for (Object obj : collection) {
			contains = contains(obj);
			if (!contains) {
				break;
			}
		}

		return contains;
	}

	@Override
	public Iterator<K> iterator() {
		return lruList.iterator();
	}

	@Override
	public boolean removeAll(Collection<?> collection) {
		boolean changed = false;

		for (Object obj : collection) {
			changed = remove(obj) || changed;
		}
		return changed;
	}

	@Override
	public boolean retainAll(Collection<?> collection) {
		boolean changed = false;
		List<K> toRemove = new ArrayList<K>();
		for (K obj : this) {
			if (!collection.contains(obj)) {
				toRemove.add(obj);
			}
		}
		
		for (K obj : toRemove) {
			changed = remove(obj) || changed;
		}
		
		return changed;
	}

	@Override
	public int size() {
		return lruList.size();
	}

	@Override
	public Object[] toArray() {
		return lruList.toArray();
	}

	@Override
	public <T> T[] toArray(T[] a) {
		return lruList.toArray(a);
	}

}
