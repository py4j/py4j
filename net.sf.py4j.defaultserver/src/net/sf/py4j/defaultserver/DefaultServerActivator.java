package net.sf.py4j.defaultserver;

import net.sf.py4j.defaultserver.preferences.PreferenceConstants;

import org.eclipse.swt.widgets.Display;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.plugin.AbstractUIPlugin;
import org.osgi.framework.BundleContext;

import py4j.GatewayServer;

public class DefaultServerActivator extends AbstractUIPlugin {

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
		super.start(bundleContext);
		DefaultServerActivator.context = bundleContext;
		activator = this;
		int defaultPort = getPreferenceStore().getInt(
				PreferenceConstants.PREF_DEFAULT_PORT);
		int defaultCallBackPort = getPreferenceStore().getInt(
				PreferenceConstants.PREF_DEFAULT_CALLBACK_PORT);
		server = new GatewayServer(this, defaultPort, defaultCallBackPort,
				GatewayServer.DEFAULT_CONNECT_TIMEOUT,
				GatewayServer.DEFAULT_READ_TIMEOUT, null);
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
		super.stop(bundleContext);
	}

	public GatewayServer getServer() {
		return server;
	}

	public static DefaultServerActivator getDefault() {
		return activator;
	}
	
	public void closeEclipse() {
		Display.getDefault().asyncExec(new Runnable() {
			public void run() {
				PlatformUI.getWorkbench().close();
			}
		});
	}

}
