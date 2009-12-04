/**
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
 */

package py4j;

import java.util.ArrayList;
import java.util.List;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

public class DefaultJavaGatewayTest {

	private ExampleGateway gateway;
	
	@Before
	public void setUp() {
		gateway = new ExampleGateway();
	}
	
	@After
	public void tearDown() {
		gateway.shutdown();
	}
	
	@Test
	public void testNoParam() {
		ReturnObject obj1 = gateway.getNewExample();
		ReturnObject obj2 = gateway.invoke("method1", obj1.getName(), null);
		assertEquals(1, obj2.getPrimitiveObject());
	}
	
	@Test
	public void testVoidMethod() {
		ReturnObject obj1 = gateway.getNewExample();
		List<Argument> args = new ArrayList<Argument>();
		args.add(new Argument("This is a String!",false));
		ReturnObject obj2 = gateway.invoke("method2", obj1.getName(), args);
		assertTrue(obj2.isNull());
	}
	
	@Test
	public void testCharMethod() {
		ReturnObject obj1 = gateway.getNewExample();
		List<Argument> args = new ArrayList<Argument>();
		args.add(new Argument('c', false));
		ReturnObject obj2 = gateway.invoke("method4", obj1.getName(), args);
		// Unfortunately, Rhino has no way of distinguishing from chars and strings.
		assertEquals(3, ((ExampleClass)gateway.getObject(obj2.getName())).getField1());
	}
	
	@Test
	public void testCharMethod2() {
		ReturnObject obj1 = gateway.getNewExample();
		List<Argument> args = new ArrayList<Argument>();
		args.add(new Argument('c', false));
		ReturnObject obj2 = gateway.invoke("method6", obj1.getName(), args);
		// Unfortunately, Rhino has no way of distinguishing from chars and strings.
		assertEquals(4, ((ExampleClass)gateway.getObject(obj2.getName())).getField1());
	}
	
	@Test
	public void testStringMethod() {
		ReturnObject obj1 = gateway.getNewExample();
		List<Argument> args = new ArrayList<Argument>();
		args.add(new Argument("c", false));
		ReturnObject obj2 = gateway.invoke("method4", obj1.getName(), args);
		assertEquals(3, ((ExampleClass)gateway.getObject(obj2.getName())).getField1());
	}
	
	@Test
	public void testUsingMethodReturn() {
		ReturnObject obj1 = gateway.getNewExample();
		List<Argument> args = new ArrayList<Argument>();
		args.add(new Argument("c", false));
		ReturnObject obj2 = gateway.invoke("method4", obj1.getName(), args);
		args = new ArrayList<Argument>();
		args.add(new Argument(obj2.getName(),true));
		ReturnObject obj3 = gateway.invoke("method5", obj1.getName(), args);
		assertEquals(2, obj3.getPrimitiveObject());
	}
	
}
