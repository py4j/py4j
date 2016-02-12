package py4j;

import java.net.Socket;

/**
 * Created by barthelemy on 2016-02-12.
 */
public interface Py4JServerConnection {

	/**
	 * @return The socket used by this gateway connection.
	 */
	Socket getSocket();

}
