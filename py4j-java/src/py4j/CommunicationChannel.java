package py4j;

import java.io.IOException;

/**
 * <p>
 * A communication channel is responsible for sending commands to the Python
 * side. This interface is used by the callback framework.
 * </p>
 * 
 * @author Barthelemy Dagenais
 * 
 */
public interface CommunicationChannel {

	public void start() throws IOException;

	public String sendCommand(String command);

	/**
	 * <p>
	 * <b>Note:</b> shutdown() should NOT throw any exception
	 * </p>
	 */
	public void shutdown();

	public boolean wasUsed();

	public void setUsed(boolean used);

}
