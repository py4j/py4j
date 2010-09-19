package py4j;

/**
 * <p>
 * Exception raised when a network error is encountered while using Py4J.
 * </p>
 * 
 * @author Barthelemy Dagenais
 * 
 */
public class Py4JNetworkException extends RuntimeException {

	/**
	 * 
	 */
	private static final long serialVersionUID = -3338931855286981212L;

	public Py4JNetworkException() {
	}

	public Py4JNetworkException(String message) {
		super(message);
	}

	public Py4JNetworkException(Throwable cause) {
		super(cause);
	}

	public Py4JNetworkException(String message, Throwable cause) {
		super(message, cause);
	}

}
