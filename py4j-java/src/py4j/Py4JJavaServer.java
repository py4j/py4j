package py4j;

import java.util.List;

/**
 * Created by barthelemy on 2016-02-10.
 */
public interface Py4JJavaServer {

	List<GatewayServerListener> getListeners();

	Gateway getGateway();

	void shutdown();
}
