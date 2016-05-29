package py4j.instrumented;

public class InstrumentedObject {

	private String name;

	public InstrumentedObject(String name) {
		this.name = name;
		MetricRegistry.addCreatedObject(this);
	}

	@Override protected void finalize() throws Throwable {
		MetricRegistry.addFinalizedObject(this);
		super.finalize();
	}
}
