package py4j;

import java.io.Closeable;
import java.net.Socket;
import java.util.logging.Level;
import java.util.logging.Logger;

public class NetworkUtil {

	private final static Logger logger = Logger.getLogger(NetworkUtil.class.getName());
	
	public static void quietlyClose(Closeable closeable) {
		try {
			if (closeable != null) {
				closeable.close();
			}
		} catch(Exception e) {
			logger.log(Level.WARNING, "Closeable cannot be closed.",e);
		}
	}
	
	public static void quietlyClose(Socket closeable) {
		try {
			if (closeable != null) {
				closeable.close();
			}
		} catch(Exception e) {
			logger.log(Level.WARNING, "Socket cannot be closed.",e);
		}
	}
	
}
