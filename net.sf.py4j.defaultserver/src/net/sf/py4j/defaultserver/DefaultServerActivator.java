package net.sf.py4j.defaultserver;

import java.io.IOException;
import java.net.DatagramSocket;
import java.net.ServerSocket;

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
		
		final boolean enabled = getPreferenceStore().getBoolean(PreferenceConstants.PREF_PY4J_ACTIVE);
		if (!enabled) return;
		
		int defaultPort = getPreferenceStore().getInt(PreferenceConstants.PREF_DEFAULT_PORT);
		int defaultCallBackPort = getPreferenceStore().getInt(PreferenceConstants.PREF_DEFAULT_CALLBACK_PORT);
		
		if (getPreferenceStore().getBoolean(PreferenceConstants.PREF_USE_SWT_DISPLAY_TREAD)) {
			
			server = new SWTGatewayServer(this, getFreePort(defaultPort), getFreePort(defaultCallBackPort),
					GatewayServer.DEFAULT_CONNECT_TIMEOUT,
					GatewayServer.DEFAULT_READ_TIMEOUT, null);
			
		} else {
			server = new GatewayServer(this, defaultPort, defaultCallBackPort,
					GatewayServer.DEFAULT_CONNECT_TIMEOUT,
					GatewayServer.DEFAULT_READ_TIMEOUT, null);
		}
		server.start();
	}
	/**
	 * Attempts to get a free port starting at the passed in port and
	 * working up.
	 * 
	 * @param startPort
	 * @return
	 */
	public static int getFreePort(final int startPort) {
		
	    int port = startPort;
	    while(!isPortFree(port)) port++;
	    	
	    return port;
	}


	/**
	 * Checks if a port is free.
	 * @param port
	 * @return
	 */
	public static boolean isPortFree(int port) {

	    ServerSocket ss = null;
	    DatagramSocket ds = null;
	    try {
	        ss = new ServerSocket(port);
	        ss.setReuseAddress(true);
	        ds = new DatagramSocket(port);
	        ds.setReuseAddress(true);
	        return true;
	    } catch (IOException e) {
	    } finally {
	        if (ds != null) {
	            ds.close();
	        }

	        if (ss != null) {
	            try {
	                ss.close();
	            } catch (IOException e) {
	                /* should not be thrown */
	            }
	        }
	    }

	    return false;
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

	/**
	 * Might be null
	 * @return
	 */
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
