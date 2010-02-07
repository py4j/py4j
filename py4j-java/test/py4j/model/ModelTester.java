package py4j.model;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

import p1.AnObject;
import p1.AnObject2;
import p1.AnObject3;
import p1.AnObject4;

public class ModelTester {

	@Test
	public void testModel() {
		Py4JClass clazz = Py4JClass.buildClass(AnObject.class);
		assertEquals(clazz.getSignature(false), "p1.AnObject");
		assertEquals(clazz.getSignature(true), "AnObject");
		assertEquals(1,clazz.getClasses().length);
		assertEquals(2,clazz.getMethods().length);
		assertEquals(1,clazz.getFields().length);
		Py4JMethod m1 = clazz.getMethods()[0];
		Py4JMethod m2 = clazz.getMethods()[1];
		Py4JField f1 = clazz.getFields()[0];
		Py4JClass clazz2 = clazz.getClasses()[0];
		assertEquals(m1.getSignature(false), "m1(java.lang.String, p1.AnObject) : void");
		assertEquals(m1.getSignature(true), "m1(String, AnObject) : void");
		assertEquals(m2.getSignature(false), "m2(int) : java.lang.String");
		assertEquals(m2.getSignature(true), "m2(int) : String");
		assertEquals(f1.getSignature(false), "value1 : java.lang.Integer");
		assertEquals(f1.getSignature(true), "value1 : Integer");
		assertEquals(clazz2.getSignature(false),"p1.AnObject$InternalClass");
		assertEquals(clazz2.getSignature(true),"AnObject$InternalClass");
	}
	
	@Test
	public void testClassWithSuper() {
		Py4JClass clazz2 = Py4JClass.buildClass(AnObject2.class);
		Py4JClass clazz3 = Py4JClass.buildClass(AnObject3.class);
		Py4JClass clazz4 = Py4JClass.buildClass(AnObject4.class);
		
		assertEquals(clazz2.getSignature(false),"p1.AnObject2 extends p1.AnObject");
		assertEquals(clazz3.getSignature(false),"p1.AnObject3 implements java.lang.Runnable, java.io.Serializable");
		assertEquals(clazz4.getSignature(false),"p1.AnObject4 extends p1.AnObject3 implements java.lang.Cloneable");
	}
	
	@Test
	public void testHelpPage() {
		Py4JClass clazz = Py4JClass.buildClass(AnObject.class);
		String helpPage = HelpPageGenerator.getHelpPage(clazz, "variable1", false);
		System.out.println("BEGIN");
		System.out.println(helpPage);
		System.out.println("END");
	}
}
