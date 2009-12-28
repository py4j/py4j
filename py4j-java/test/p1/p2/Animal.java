package p1.p2;

import p1.Cat;

public class Animal {

	private int age = 10;
	
	public String age2 = "";
	
	public Animal() {
		System.out.println("Animal");
	}
	
	public Animal(String s) {
		System.out.println("Animal1");
	}
	
	public void meow(String s, int i) {
		System.out.println("meowmeow");
	}
	
	public int age() {
		return this.age;
	}
	
	public void meow(String s) {
		System.out.println("meowstring");
	}
	
	public void meow(char s) {
		System.out.println("meowchar");
	}
	
	public void meow(int s) {
		System.out.println("meowint");
	}
	
	public void meow(long s) {
		System.out.println("meowlong");
	}
	
	public void meow(boolean s) {
		System.out.println("meowbool");
	}
	
	public void meow(Object o) {
		System.out.println("meowobject");
	}
	
	public void meow(Animal a) {
		System.out.println("meowanim");
	}
	
	public void meow(Cat a) {
		System.out.println("meowcat");
	}
	
}
