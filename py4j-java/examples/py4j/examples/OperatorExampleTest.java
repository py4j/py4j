package py4j.examples;

import java.net.InetAddress;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.concurrent.TimeUnit;

import py4j.CallbackClient;
import py4j.GatewayServer;

public class OperatorExampleTest {
	private final static int MAX = 1000;

	public List<Integer> randomBinaryOperator(Operator op) {
		Random random = new Random();
		List<Integer> numbers = new ArrayList<Integer>();
		numbers.add(random.nextInt(MAX));
		numbers.add(random.nextInt(MAX));
		numbers.add(op.doOperation(numbers.get(0), numbers.get(1)));
		return numbers;
	}

	public List<Integer> randomTernaryOperator(Operator op) {
		Random random = new Random();
		List<Integer> numbers = new ArrayList<Integer>();
		numbers.add(random.nextInt(MAX));
		numbers.add(random.nextInt(MAX));
		numbers.add(random.nextInt(MAX));
		numbers.add(op.doOperation(numbers.get(0), numbers.get(1),
				numbers.get(2)));
		return numbers;
	}

	public static void main(String[] args) {
		try {
			CallbackClient cbClient = new CallbackClient(
					GatewayServer.DEFAULT_PYTHON_PORT,
					InetAddress.getByName("localhost"), 2, TimeUnit.SECONDS);
			GatewayServer server = new GatewayServer(new OperatorExample(),
					GatewayServer.DEFAULT_PORT,
					GatewayServer.DEFAULT_CONNECT_TIMEOUT,
					GatewayServer.DEFAULT_READ_TIMEOUT, null, cbClient);
			server.start();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
}
