package net.sf.py4j.defaultserver;

import org.osgi.framework.BundleActivator;
import org.osgi.framework.BundleContext;

import py4j.GatewayServer;

public class DefaultServerActivator implements BundleActivator {

	private static BundleContext context;

	private static DefaultServerActivator activator;

	private GatewayServer server;

	static BundleContext getContext() {
		return context;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.osgi.framework.BundleActivator#start(org.osgi.framework.BundleContext
	 * )
	 */
	public void start(BundleContext bundleContext) throws Exception {
		DefaultServerActivator.context = bundleContext;
		activator = this;
		server = new GatewayServer(this);
		server.start();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.osgi.framework.BundleActivator#stop(org.osgi.framework.BundleContext)
	 */
	public void stop(BundleContext bundleContext) throws Exception {
		if (server != null) {
			server.shutdown();
		}
		context = null;
		activator = null;
	}

	public GatewayServer getServer() {
		return server;
	}

	public static DefaultServerActivator getDefault() {
		return activator;
	}

}
