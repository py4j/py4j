package py4j.model;

public abstract class Py4JMember {

	// Currently not supported
	private final String javadoc;
	
	private final String name;

	public Py4JMember(String name, String javadoc) {
		super();
		this.name = name;
		this.javadoc = javadoc;
	}
	
	public String getJavadoc() {
		return javadoc;
	}

	public String getName() {
		return name;
	}
	
	public abstract String getSignature(boolean shortName);
	
}
