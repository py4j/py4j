package py4j.examples;

public class ReturnerExample {

	public float computeFloat(IReturnConverter returner) {
		return returner.getFloat();
	}

	public char computeChar(IReturnConverter returner) {
		return returner.getChar();
	}

	public int computeNothing(IReturnConverter returner) {
		return 1;
	}
}
