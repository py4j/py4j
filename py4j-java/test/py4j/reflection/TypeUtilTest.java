package py4j.reflection;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

public class TypeUtilTest {

	@Test
	public void testDistance() {
		assertEquals(0, TypeUtil.computeDistance(A.class, A.class));
		assertEquals(1, TypeUtil.computeDistance(A.class, B.class));
		assertEquals(2, TypeUtil.computeDistance(A.class, C.class));
		assertEquals(3, TypeUtil.computeDistance(A.class, D.class));
		assertEquals(4, TypeUtil.computeDistance(Object.class, D.class));
		assertEquals(-1, TypeUtil.computeDistance(int.class, D.class));
		assertEquals(-1, TypeUtil.computeDistance(String.class, D.class));
		assertEquals(1, TypeUtil.computeDistance(I0.class, I1.class));
		assertEquals(1, TypeUtil.computeDistance(I0.class, V.class));
		assertEquals(2, TypeUtil.computeDistance(I0.class, W.class));
		assertEquals(1, TypeUtil.computeDistance(I1.class, W.class));
		assertEquals(1, TypeUtil.computeDistance(I0.class, X.class));
		assertEquals(2, TypeUtil.computeDistance(I0.class, Y.class));
		assertEquals(3, TypeUtil.computeDistance(J0.class, Y.class));
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
