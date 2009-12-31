/*******************************************************************************
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
package py4j.reflection;

import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertEquals;

import org.junit.Before;
import org.junit.Test;

import p1.Cat;

public class ReflectionEngineTest {

	private ReflectionEngine rEngine;
	
	@Before
	public void setUp() {
		rEngine = new ReflectionEngine();
	}
	
	@Test
	public void testGetField() {
		Cat cat = new Cat();
		// Private from super
		assertNull(rEngine.getField(cat, "age"));
		
		// Inexistent
		assertNull(rEngine.getField(cat, "age1"));
		
		// Field shadowing
		assertEquals(rEngine.getField(cat, "age2").getType(),int.class);
		assertEquals(rEngine.getField(Cat.class, "age2").getType(),int.class);
		assertEquals(rEngine.getField("p1.Cat", "age2").getType(),int.class);
		
		// Static field
		assertEquals(rEngine.getField(cat, "CONSTANT").getType(),String.class);
		
		// Package 
		assertNull(rEngine.getField(cat, "age4"));
		
		// Protected
		assertNull(rEngine.getField(cat, "age5"));
	}
	
	@Test
	public void testGetFieldValue() {
		Cat cat = new Cat();
		
		assertEquals(rEngine.getFieldValue(cat, rEngine.getField(cat, "age2")), 2);
		assertEquals(rEngine.getFieldValue(cat, rEngine.getField(cat, "CONSTANT")), "Salut!");
		assertEquals(rEngine.getFieldValue(null, rEngine.getField(cat, "CONSTANT")), "Salut!");
	}
	
}
