package py4j;

import java.util.List;

public class DefaultSynchronizedGateway extends DefaultGateway {

	@Override
	public synchronized ReturnObject invoke(String methodName, String targetObjectId,
			List<Argument> args) {
		return super.invoke(methodName, targetObjectId, args);
	}
	
}
