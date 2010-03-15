package py4j;

import java.io.IOException;

public interface CommunicationChannel {

	public void start() throws IOException;
	
	public String sendCommand(String command);
	
	/**
	 * <p><b>Note:</b> shutdown() should NOT throw any exception</p>
	 */
	public void shutdown();
	
	public boolean wasUsed();
	
	public void setUsed(boolean used);

}
