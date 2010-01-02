/*******************************************************************************
 * Copyright (c) 2010, Barthelemy Dagenais All rights reserved.
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

import static org.junit.Assert.assertEquals;

import org.junit.Test;

public class TypeUtilTest {

	@Test
	public void testDistance() {
		assertEquals(0, TypeUtil.computeDistance(A.class, A.class));
		assertEquals(100, TypeUtil.computeDistance(A.class, B.class));
		assertEquals(200, TypeUtil.computeDistance(A.class, C.class));
		assertEquals(300, TypeUtil.computeDistance(A.class, D.class));
		assertEquals(400, TypeUtil.computeDistance(Object.class, D.class));
		assertEquals(-1, TypeUtil.computeDistance(int.class, D.class));
		assertEquals(-1, TypeUtil.computeDistance(String.class, D.class));
		assertEquals(100, TypeUtil.computeDistance(I0.class, I1.class));
		assertEquals(100, TypeUtil.computeDistance(I0.class, V.class));
		assertEquals(200, TypeUtil.computeDistance(I0.class, W.class));
		assertEquals(100, TypeUtil.computeDistance(I1.class, W.class));
		assertEquals(100, TypeUtil.computeDistance(I0.class, X.class));
		assertEquals(200, TypeUtil.computeDistance(I0.class, Y.class));
		assertEquals(300, TypeUtil.computeDistance(J0.class, Y.class));
	}
}

class A {
	
}

class B extends A {
	
}

class C extends B {
	
}

class D extends C {
	
}

interface I0 {
	
}

interface I1 extends I0 {
	
}

interface I2 extends I1 {
	
}

interface J0 {
	
}

class V implements I0, J0 {
	
}

class W extends V implements I1 {
	
}

class X extends V implements I0 {
	
}

class Y extends X implements I2 {
	
}
