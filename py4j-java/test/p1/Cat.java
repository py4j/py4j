package p1;

import p1.p2.Animal;

public class Cat extends Animal {
	
	public int age2 = 2;
	
	public static final String CONSTANT = "Salut!";
	
	public static void meowmeow(String s) {
		System.out.println("meowmoewcat");
	}
	
	public void meow(long s) {
		System.out.println("meowlongcat");
	}
	
	public void meow(boolean s) {
		System.out.println("meowboolcat");
	}
	
	public void meow(Object o) {
		System.out.println("meowobjectcat");
	}
	
	private void meow2(Cat cat) {
		System.out.println("meowcatcat");
	}
	
	protected void meow3(Cat cat) {
		System.out.println("meowcatcat");
	}
	
	void meow4(Cat cat) {
		System.out.println("meowcatcat");
	}
	
	public void meow5(String s1, String s2) {
		System.out.println("Meowing: " + s1 + s2);
	}
	
	
}
