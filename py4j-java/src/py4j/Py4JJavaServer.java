package py4j;

/**
 * Created by barthelemy on 2016-02-10.
 */
public interface Py4JJavaServer {

	Gateway getGateway();

	void shutdown();
}
