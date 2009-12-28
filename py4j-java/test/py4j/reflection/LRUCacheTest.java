package py4j.reflection;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNull;

import org.junit.Test;

public class LRUCacheTest {

	@Test
	public void testCacheSize() {
		LRUCache<String, String> cache = new LRUCache<String, String>(5);
		cache.put("1", "1v");
		cache.put("2", "2v");
		cache.put("3", "3v");
		cache.put("4", "4v");
		cache.put("5", "5v");
		assertEquals(cache.size(), 5);
		assertEquals(cache.getLRUList().size(), 5);
		cache.put("6", "6v");
		assertEquals(cache.size(), 5);
		assertEquals(cache.getLRUList().size(), 5);
		assertEquals(cache.getLRUList().get(0),"6");
		assertEquals(cache.getLRUList().get(4),"2");
		assertNull(cache.get("1"));
	}
	
}
