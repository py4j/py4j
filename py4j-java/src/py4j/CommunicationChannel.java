package py4j;

public interface CommunicationChannel {

	public String sendCommand(String command);
	
	public void shutdown();
	
}
