package py4j.reflection;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;

import java.util.ArrayList;
import java.util.List;

import org.junit.Test;

public class LRUCacheTest {

	@Test
	public void testCacheSize() {
		LRUCache<String> cache = new LRUCache<String>(5);
		cache.add("1");
		cache.add("2");
		cache.add("3");
		cache.add("4");
		cache.add("5");
		assertEquals(cache.size(), 5);
		cache.add("6");
		assertEquals(cache.size(), 5);
		assertEquals(cache.getLRUList().get(0),"6");
		assertEquals(cache.getLRUList().get(4),"2");
		assertNull(cache.get("1"));
		
		assertTrue(cache.contains("2"));
		assertFalse(cache.contains("1"));
		
		cache.remove("2");
		assertEquals(cache.size(), 4);
		assertEquals(cache.getLRUList().size(), 4);
		assertEquals(cache.getLRUList().get(0),"6");
		assertEquals(cache.getLRUList().get(3),"3");
		
		List<String> list = new ArrayList<String>();
		list.add("3");
		list.add("6");
		assertTrue(cache.containsAll(list));
		assertTrue(cache.retainAll(list));
		assertEquals(2, cache.size());
		
		assertFalse(cache.addAll(list));
		assertTrue(cache.removeAll(list));
		assertEquals(0, cache.size());
	}
	
}
