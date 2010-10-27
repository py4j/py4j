package net.sf.py4j.defaultserver.preferences;

import org.eclipse.jface.preference.*;
import org.eclipse.ui.IWorkbenchPreferencePage;
import org.eclipse.ui.IWorkbench;
import net.sf.py4j.defaultserver.DefaultServerActivator;

/**
 * This class represents a preference page that
 * is contributed to the Preferences dialog. By 
 * subclassing <samp>FieldEditorPreferencePage</samp>, we
 * can use the field support built into JFace that allows
 * us to create a page that is small and knows how to 
 * save, restore and apply itself.
 * <p>
 * This page is used to modify preferences only. They
 * are stored in the preference store that belongs to
 * the main plug-in class. That way, preferences can
 * be accessed directly via the preference store.
 */

public class DefaultServerPreferencePage
	extends FieldEditorPreferencePage
	implements IWorkbenchPreferencePage {

	public DefaultServerPreferencePage() {
		super(GRID);
		setPreferenceStore(DefaultServerActivator.getDefault().getPreferenceStore());
		setDescription("Py4J Default Server Preference Page");
	}
	
	/**
	 * Creates the field editors. Field editors are abstractions of
	 * the common GUI blocks needed to manipulate various types
	 * of preferences. Each field editor knows how to save and
	 * restore itself.
	 */
	public void createFieldEditors() {
		addField(new IntegerFieldEditor(PreferenceConstants.PREF_DEFAULT_PORT, 
				"TCP Port (requires Eclipse restart):", getFieldEditorParent()));
		addField(new IntegerFieldEditor(PreferenceConstants.PREF_DEFAULT_CALLBACK_PORT, 
				"Callback TCP Port (requires Eclipse restart):", getFieldEditorParent()));
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ui.IWorkbenchPreferencePage#init(org.eclipse.ui.IWorkbench)
	 */
	public void init(IWorkbench workbench) {
	}
	
}