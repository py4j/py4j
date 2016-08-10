package p1;

public class VarArgTester {
	int called;
	
	public VarArgTester(int a) {
		called = 0;
	}

	public VarArgTester(int... as) {
		called = 1;
	}

	public VarArgTester(float s, int... as) {
		called = 2;
	}

	public int method1() {
		return 1;
	}

	public int method1(int b) {
		return 2;
	}

	public int method1(int... bs) {
		return 3;
	}

	public int method1(float s, int... bs) {
		return 4;
	}

	public int called() {
		return called;
	}
}