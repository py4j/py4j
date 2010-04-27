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

package py4j.examples;

import java.util.ArrayList;
import java.util.List;

public class ExampleClass {

	private int field1 = 2;
	
	public int field10 = 10;
	
	public StringBuffer field20 = new StringBuffer();
	
	public StringBuffer field21;
	
	public ExampleClass() {
		
	}
	
	public ExampleClass(int field1) {
		this.field1 = field1;
	}
	
	public int method1() {
		return 1;
	}
	
	public void method2(String param1) {
		
	}
	
	public List<String> getList(int i) {
		List<String> list = new ArrayList<String>();
		for (int counter = 0; counter < i; counter++) {
			list.add(""+counter);
		}
		return list;
	}
	
	public String method3(int param1, boolean param2) {
		return "Hello World";
	}
	
	public ExampleClass method4(char param1) {
		ExampleClass ex = new ExampleClass();
		ex.field1 = 1;
		return ex;
	}
	
	public ExampleClass method4(String param1) {
		ExampleClass ex = new ExampleClass();
		ex.field1 = 3;
		return ex;
	}
	
	public int method5(ExampleClass param1) {
		return 2;
	}

	public int getField1() {
		return field1;
	}

	public void setField1(int field1) {
		this.field1 = field1;
	}
	
	public ExampleClass method6(char param1) {
		ExampleClass ex = new ExampleClass();
		ex.field1 = 4;
		return ex;
	}
	
	public Object[] getStringArray() {
		return new String[] {"222","111","333"};
	}
	
	public int[] getIntArray() {
		return new int[] {2, 5, 1, 10};
	}
	
	public String callHello(IHello hello) {
		return hello.sayHello();
	}
	
	public String callHello2(IHello hello) {
		return hello.sayHello(10,"MyMy!\n;");
	}
}
