package net.sf.py4j.defaultserver;

import java.util.concurrent.CountDownLatch;

import org.eclipse.equinox.app.IApplication;
import org.eclipse.equinox.app.IApplicationContext;

import py4j.GatewayConnection;
import py4j.GatewayServer;
import py4j.GatewayServerListener;

public class HeadlessApplication implements IApplication, GatewayServerListener {
	
	private CountDownLatch latch;
	
	@Override
	public Object start(IApplicationContext context) throws Exception {
		GatewayServer server = DefaultServerActivator.getDefault().getServer();
		latch = new CountDownLatch(1);
		server.addListener(this);
		System.out.println("Py4J Headless Application Started.");
		Object result = IApplication.EXIT_OK;
		try {
			latch.await();
		} catch(Exception e) {
			result = new Integer(1);
		}
		return result;
	}

	@Override
	public void stop() {

	}

	@Override
	public void serverStarted() {
		
	}

	@Override
	public void serverStopped() {
		
	}

	@Override
	public void serverError(Exception e) {
		
	}

	@Override
	public void serverPreShutdown() {
		
	}

	@Override
	public void serverPostShutdown() {
		System.out.println("Py4J Headless Application Stopping.");
		latch.countDown();
	}

	@Override
	public void connectionStarted(GatewayConnection gatewayConnection) {
		
	}

	@Override
	public void connectionStopped(GatewayConnection gatewayConnection) {
		
	}

	@Override
	public void connectionError(Exception e) {
		
	}
	
	

}
