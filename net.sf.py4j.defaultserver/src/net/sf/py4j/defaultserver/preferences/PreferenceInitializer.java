package net.sf.py4j.defaultserver.preferences;

import org.eclipse.core.runtime.preferences.AbstractPreferenceInitializer;
import org.eclipse.jface.preference.IPreferenceStore;

import py4j.GatewayServer;

import net.sf.py4j.defaultserver.DefaultServerActivator;

/**
 * Class used to initialize default preference values.
 */
public class PreferenceInitializer extends AbstractPreferenceInitializer {

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.core.runtime.preferences.AbstractPreferenceInitializer#initializeDefaultPreferences()
	 */
	public void initializeDefaultPreferences() {
		IPreferenceStore store = DefaultServerActivator.getDefault().getPreferenceStore();
		boolean active = Boolean.getBoolean(PreferenceConstants.PREF_PY4J_ACTIVE); // They can override the default using -DPREF_PY4J_ACTIVE=...
		store.setDefault(PreferenceConstants.PREF_PY4J_ACTIVE, active);
		store.setDefault(PreferenceConstants.PREF_DEFAULT_PORT, GatewayServer.DEFAULT_PORT);
		store.setDefault(PreferenceConstants.PREF_DEFAULT_CALLBACK_PORT, GatewayServer.DEFAULT_PYTHON_PORT);
		// Optional setting to call all API in the SWT thread which allows UI calls to be done.
		store.setDefault(PreferenceConstants.PREF_USE_SWT_DISPLAY_THREAD, false);
		// Optional setting to use external class loader provided by a service
		store.setDefault(PreferenceConstants.PREF_USE_EXTERNAL_CLASS_LOADER_SERVICE, true);
	}

}
