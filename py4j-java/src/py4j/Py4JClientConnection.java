package py4j;

import java.io.IOException;

/**
 * Created by barthelemy on 2016-02-12.
 */
public interface Py4JClientConnection {

	String sendCommand(String command);

	String sendCommand(String command, boolean blocking);

	void shutdown();

	void start() throws IOException;

	void setUsed(boolean used);

	boolean wasUsed();

}
