package py4j;

public class ConnectionProperty {

	private boolean cleanConnection;

	public ConnectionProperty() {
		this(true);
	}
	
	public ConnectionProperty(boolean cleanConnection) {
		super();
		this.cleanConnection = cleanConnection;
	}

	public boolean isCleanConnection() {
		return cleanConnection;
	}

	public void setCleanConnection(boolean cleanConnection) {
		this.cleanConnection = cleanConnection;
	}
	
	
	
}
