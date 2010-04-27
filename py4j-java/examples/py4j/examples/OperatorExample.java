package py4j.examples;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

import py4j.GatewayServer;

public class OperatorExample {

	public List<Integer> randomBinaryOperator(Operator op) {
		Random random = new Random();
		List<Integer> numbers = new ArrayList<Integer>();
		numbers.add(random.nextInt());
		numbers.add(random.nextInt());
		numbers.add(op.doOperation(numbers.get(0), numbers.get(1)));
		return numbers;
	}
	
	public List<Integer> randomTernaryOperator(Operator op) {
		Random random = new Random();
		List<Integer> numbers = new ArrayList<Integer>();
		numbers.add(random.nextInt());
		numbers.add(random.nextInt());
		numbers.add(random.nextInt());
		numbers.add(op.doOperation(numbers.get(0), numbers.get(1), numbers.get(2)));
		return numbers;
	}
	
	public static void main(String[] args) {
		GatewayServer server = new GatewayServer(new OperatorExample());
		server.start();
	}

}
