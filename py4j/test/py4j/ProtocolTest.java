/*******************************************************************************
 * 
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
 *******************************************************************************/
package py4j;

import org.junit.Test;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

public class ProtocolTest {

	@Test
	public void testEmpty() {
		assertTrue(Protocol.isEmpty(""));
		assertTrue(Protocol.isEmpty("  "));
		assertTrue(Protocol.isEmpty("\n"));
		assertTrue(Protocol.isEmpty(null));
		assertFalse(Protocol.isEmpty("b:true"));
	}

	@Test
	public void testIntegers() {
		assertTrue(Protocol.isInteger("i:123"));
		assertFalse(Protocol.isInteger("b:true"));
		try {
			Protocol.isInteger(null);
			fail();
		} catch (NullPointerException e) {
			assertTrue(true);
		}
		try {
			Protocol.isInteger("");
			fail();
		} catch (Exception e) {
			assertTrue(true);
		}
		try {
			Protocol.getInteger("i:");
			fail();
		} catch (Exception e) {
			assertTrue(true);
		}
		assertEquals(1, Protocol.getInteger("i:1"));
		assertEquals(234, Protocol.getInteger("i:234"));
	}

	@Test
	public void testBooleans() {
		assertTrue(Protocol.isBoolean("b:true"));
		assertFalse(Protocol.isBoolean("i:234"));
		try {
			Protocol.isBoolean(null);
			fail();
		} catch (NullPointerException e) {
			assertTrue(true);
		}
		try {
			Protocol.isBoolean("");
			fail();
		} catch (Exception e) {
			assertTrue(true);
		}
		assertEquals(true, Protocol.getBoolean("b:true"));
		assertEquals(true, Protocol.getBoolean("b:True"));
		assertEquals(false, Protocol.getBoolean("b:false"));
		assertEquals(false, Protocol.getBoolean("b:False"));
		assertEquals(false, Protocol.getBoolean("b:1"));
		assertEquals(false, Protocol.getBoolean("b:"));
	}

	@Test
	public void testStrings() {
		assertTrue(Protocol.isString("s:hello"));
		assertFalse(Protocol.isString("i:234"));
		try {
			Protocol.isString(null);
			fail();
		} catch (NullPointerException e) {
			assertTrue(true);
		}
		try {
			Protocol.isString("");
			fail();
		} catch (Exception e) {
			assertTrue(true);
		}
		assertEquals("", Protocol.getString("s:"));
		assertEquals("Hello\nWorld\t", Protocol.getString("s:Hello\\nWorld\t"));
	}

	@Test
	public void testReferences() {
		assertTrue(Protocol.isReference("r:o123"));
		assertFalse(Protocol.isReference("b:true"));
		try {
			Protocol.isReference(null);
			fail();
		} catch (NullPointerException e) {
			assertTrue(true);
		}
		try {
			Protocol.isReference("");
			fail();
		} catch (Exception e) {
			assertTrue(true);
		}
		try {
			Protocol.getReference("r:");
			fail();
		} catch (Exception e) {
			assertTrue(true);
		}
		assertEquals("o123", Protocol.getReference("r:o123"));
		assertEquals("o2", Protocol.getReference("r:o2"));
	}

	@Test
	public void testDoubles() {
		assertTrue(Protocol.isDouble("d:1.2"));
		assertFalse(Protocol.isDouble("b:true"));
		try {
			Protocol.isDouble(null);
			fail();
		} catch (NullPointerException e) {
			assertTrue(true);
		}
		try {
			Protocol.isDouble("");
			fail();
		} catch (Exception e) {
			assertTrue(true);
		}
		try {
			Protocol.getDouble("d:");
			fail();
		} catch (Exception e) {
			assertTrue(true);
		}
		assertEquals(1.25, Protocol.getDouble("d:1.25"), 0.001);
		assertEquals(0.0, Protocol.getDouble("d:0"), 0.001);
		assertEquals(1234.567, Protocol.getDouble("d:1234.567"), 0.001);
	}

	@Test
	public void testEnd() {
		assertTrue(Protocol.isEnd("e"));
		assertFalse(Protocol.isEnd(""));
		assertFalse(Protocol.isEnd("b:true"));
		try {
			Protocol.isEnd(null);
			fail();
		} catch (NullPointerException e) {
			assertTrue(true);
		}
	}

	@Test
	public void testNull() {
		assertTrue(Protocol.isNull("n"));
		assertFalse(Protocol.isNull("b:true"));
		try {
			Protocol.isNull("");
			fail();
		} catch (Exception e) {
			assertTrue(true);
		}
		try {
			Protocol.isNull(null);
			fail();
		} catch (NullPointerException e) {
			assertTrue(true);
		}
		assertNull(Protocol.getNull("n"));
		// Although the isNull would thrown an exception, getNull is really
		// dummy, which should not be a problem...
		assertNull(Protocol.getNull(""));
		assertNull(Protocol.getNull(null));
	}
	
	@Test
	public void testGetObject() {
		assertEquals(1, Protocol.getObject("i:1"));
		assertEquals(true, Protocol.getObject("b:True"));
		assertEquals(1.234,(Double)Protocol.getObject("d:1.234"),0.001);
		assertEquals("o123",Protocol.getObject("r:o123"));
		assertEquals("Hello\nWorld\t", Protocol.getObject("s:Hello\\nWorld\t"));
		assertNull(Protocol.getObject("n"));
		try {
			Protocol.getObject(null);
			fail();
		} catch (Py4JException e) {
			assertTrue(true);
		}
		try {
			Protocol.getObject("");
			fail();
		} catch (Py4JException e) {
			assertTrue(true);
		}
		try {
			Protocol.getObject("e");
			fail();
		} catch (Py4JException e) {
			assertTrue(true);
		}
		try {
			Protocol.getObject("z:123");
			fail();
		} catch (Py4JException e) {
			assertTrue(true);
		}
	}
	
	@Test
	public void testGetOutputCommand() {
		ReturnObject rObject1 = ReturnObject.getErrorReturnObject();
		ReturnObject rObject2 = ReturnObject.getPrimitiveReturnObject(2);
		ReturnObject rObject3 = ReturnObject.getPrimitiveReturnObject(2.2);
		ReturnObject rObject4 = ReturnObject.getPrimitiveReturnObject(2.2f);
		ReturnObject rObject5 = ReturnObject.getPrimitiveReturnObject('c');
		ReturnObject rObject6 = ReturnObject.getPrimitiveReturnObject("Hello\nWorld");
		ReturnObject rObject7 = ReturnObject.getPrimitiveReturnObject(5L);
		ReturnObject rObject8 = ReturnObject.getPrimitiveReturnObject(true);
		ReturnObject rObject9 = ReturnObject.getPrimitiveReturnObject(false);
		ReturnObject rObject10 = ReturnObject.getNullReturnObject();
		ReturnObject rObject11 = ReturnObject.getReferenceReturnObject("o123");
		
		assertEquals("x", Protocol.getOutputCommand(rObject1));
		assertEquals("yi2", Protocol.getOutputCommand(rObject2));
		assertEquals("yd2.2", Protocol.getOutputCommand(rObject3));
		assertEquals("yd2.2", Protocol.getOutputCommand(rObject4));
		assertEquals("ysc", Protocol.getOutputCommand(rObject5));
		assertEquals("ysHello\nWorld", Protocol.getOutputCommand(rObject6));
		assertEquals("yi5", Protocol.getOutputCommand(rObject7));
		assertEquals("ybtrue", Protocol.getOutputCommand(rObject8));
		assertEquals("ybfalse", Protocol.getOutputCommand(rObject9));
		assertEquals("yn", Protocol.getOutputCommand(rObject10));
		assertEquals("yro123", Protocol.getOutputCommand(rObject11));
	}

}
