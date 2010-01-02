/**
 * Copyright (c) 2009, 2010, Barthelemy Dagenais All rights reserved.
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

import py4j.examples.ExampleClass;
import py4j.examples.ExampleEntryPoint;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

public class DefaultJavaGatewayTest {

	private Gateway gateway;
	private ExampleEntryPoint entryPoint;

	@Before
	public void setUp() {
		entryPoint = new ExampleEntryPoint();
		gateway = new Gateway(entryPoint);
	}

	@After
	public void tearDown() {
		gateway.shutdown();
	}

	@Test
	public void testNoParam() {
		String name = gateway.putNewObject(entryPoint.getNewExample());
		ReturnObject obj2 = gateway.invoke("method1", name, null);
		assertEquals(1, obj2.getPrimitiveObject());
	}

	@Test
	public void testVoidMethod() {
		String name = gateway.putNewObject(entryPoint.getNewExample());
		List<Argument> args = new ArrayList<Argument>();
		args.add(new Argument("This is a String!", false));
		ReturnObject obj2 = gateway.invoke("method2", name, args);
		assertTrue(obj2.isNull());
	}

	@Test
	public void testMethodWithParams() {
		String name = gateway.putNewObject(entryPoint.getNewExample());
		List<Argument> args = new ArrayList<Argument>();
		args.add(new Argument(1, false));
		args.add(new Argument(false, false));
		ReturnObject obj2 = gateway.invoke("method3", name, args);
		assertEquals("Hello World", obj2.getPrimitiveObject());
	}

	@Test
	public void testCharMethod() {
		String name = gateway.putNewObject(entryPoint.getNewExample());
		List<Argument> args = new ArrayList<Argument>();
		args.add(new Argument('c', false));
		ReturnObject obj2 = gateway.invoke("method4", name, args);
		// Unfortunately, Rhino has no way of distinguishing from chars and
		// strings.
		assertEquals(3, ((ExampleClass) gateway.getObject(obj2.getName()))
				.getField1());
	}

	@Test
	public void testCharMethod2() {
		String name = gateway.putNewObject(entryPoint.getNewExample());
		List<Argument> args = new ArrayList<Argument>();
		args.add(new Argument('c', false));
		ReturnObject obj2 = gateway.invoke("method6", name, args);
		// Unfortunately, Rhino has no way of distinguishing from chars and
		// strings.
		assertEquals(4, ((ExampleClass) gateway.getObject(obj2.getName()))
				.getField1());
	}

	@Test
	public void testStringMethod() {
		String name = gateway.putNewObject(entryPoint.getNewExample());
		List<Argument> args = new ArrayList<Argument>();
		args.add(new Argument("c", false));
		ReturnObject obj2 = gateway.invoke("method4", name, args);
		assertEquals(3, ((ExampleClass) gateway.getObject(obj2.getName()))
				.getField1());
	}

	@Test
	public void testUsingMethodReturn() {
		String name = gateway.putNewObject(entryPoint.getNewExample());
		List<Argument> args = new ArrayList<Argument>();
		args.add(new Argument("c", false));
		ReturnObject obj2 = gateway.invoke("method4", name, args);
		args = new ArrayList<Argument>();
		args.add(new Argument(obj2.getName(), true));
		ReturnObject obj3 = gateway.invoke("method5", name, args);
		assertEquals(2, obj3.getPrimitiveObject());
	}

	@Test
	public void testGetMethodsAsString() {
		String name = gateway.putNewObject(entryPoint.getNewExample());
		Object obj = gateway.getObject(name);
		String methods = gateway.getMethodNamesAsString(obj);
		assertEquals(
				"getClass,equals,getField1,hashCode,method6,setField1,method5,wait,method4,method3,method2,method1,notify,getList,toString,notifyAll,",
				methods);
	}

	@SuppressWarnings("unchecked")
	@Test
	public void testListMethod() {
		String name = gateway.putNewObject(entryPoint.getNewExample());
		List<Argument> args = new ArrayList<Argument>();
		args.add(new Argument("3", false));
		ReturnObject obj2 = gateway.invoke("getList", name, args);
		List<String> myList = (List<String>) gateway.getObject(obj2.getName());
		assertEquals(myList.size(), 3);

		args = new ArrayList<Argument>();
		args.add(new Argument("\"3\"", false));
		gateway.invoke("add", obj2.getName(), args);
		assertEquals(myList.size(), 4);
	}

}
