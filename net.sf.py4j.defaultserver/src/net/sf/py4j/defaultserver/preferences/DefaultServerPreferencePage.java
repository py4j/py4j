package net.sf.py4j.defaultserver.preferences;

import net.sf.py4j.defaultserver.DefaultServerActivator;

import org.eclipse.core.commands.ExecutionEvent;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.jface.dialogs.ErrorDialog;
import org.eclipse.jface.preference.BooleanFieldEditor;
import org.eclipse.jface.preference.FieldEditorPreferencePage;
import org.eclipse.jface.preference.IntegerFieldEditor;
import org.eclipse.jface.util.PropertyChangeEvent;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.IWorkbench;
import org.eclipse.ui.IWorkbenchCommandConstants;
import org.eclipse.ui.IWorkbenchPreferencePage;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.commands.ICommandService;

/**
 * This class represents a preference page that is contributed to the
 * Preferences dialog. By subclassing <samp>FieldEditorPreferencePage</samp>, we
 * can use the field support built into JFace that allows us to create a page
 * that is small and knows how to save, restore and apply itself.
 * <p>
 * This page is used to modify preferences only. They are stored in the
 * preference store that belongs to the main plug-in class. That way,
 * preferences can be accessed directly via the preference store.
 */

public class DefaultServerPreferencePage extends FieldEditorPreferencePage
		implements IWorkbenchPreferencePage {

	private IntegerFieldEditor tcpPort, callPort;
	private BooleanFieldEditor swt, active;
	private LabelFieldEditor info;

	public DefaultServerPreferencePage() {
		super(GRID);
		setPreferenceStore(DefaultServerActivator.getDefault()
				.getPreferenceStore());
		/**
		 * Important do not use the term 'eclipse'. These plugins can be reused
		 * in any RCP product.
		 */
		setDescription("Py4J Default Server Preference Page.\nPlease restart after making any changes to these properties.");
	}

	/**
	 * Creates the field editors. Field editors are abstractions of the common
	 * GUI blocks needed to manipulate various types of preferences. Each field
	 * editor knows how to save and restore itself.
	 */
	public void createFieldEditors() {

		// Spacer
		new Label(getFieldEditorParent(), SWT.NONE);

		this.active = new BooleanFieldEditor(
				PreferenceConstants.PREF_PY4J_ACTIVE, "Py4j active",
				getFieldEditorParent());
		addField(active);

		this.tcpPort = new IntegerFieldEditor(
				PreferenceConstants.PREF_DEFAULT_PORT, "TCP Port",
				getFieldEditorParent());
		addField(tcpPort);

		this.callPort = new IntegerFieldEditor(
				PreferenceConstants.PREF_DEFAULT_CALLBACK_PORT,
				"Callback TCP Port", getFieldEditorParent());
		addField(callPort);

		this.swt = new BooleanFieldEditor(
				PreferenceConstants.PREF_USE_SWT_DISPLAY_THREAD,
				"Run calls in SWT Thread", getFieldEditorParent());
		addField(swt);

		this.info = new LabelFieldEditor(
				"NOTE: using the pydev python console and SWT threading can, rarely, give an unexpected error.\nPlease use an ordinary shell-based python to avoid this should you encounter it.",
				getFieldEditorParent());
		addField(info);

		// Spacer
		new Label(getFieldEditorParent(), SWT.NONE);
		new Label(getFieldEditorParent(), SWT.NONE);

		/**
		 * Restart always enabled, you have to restart after switching off too.
		 */
		Button restartButton = new Button(getFieldEditorParent(), SWT.NONE);
		restartButton.setText("Restart now");
		restartButton.addSelectionListener(new SelectionAdapter() {
			public void widgetSelected(SelectionEvent e) {
				try {
					performOk();
					ICommandService service = (ICommandService) PlatformUI
							.getWorkbench().getService(ICommandService.class);
					service.getCommand(IWorkbenchCommandConstants.FILE_RESTART)
							.executeWithChecks(new ExecutionEvent());
				} catch (Throwable t) {
					Status status = new Status(IStatus.ERROR,
							"net.sf.py4j.defaultserver", "Unable to restart", t);
					ErrorDialog.openError(
							Display.getDefault().getActiveShell(),
							"Unable to restart",
							"Currently unable to restart eclipse.", status);
				}
			}
		});

		updateEnabled(getPreferenceStore().getBoolean(
				PreferenceConstants.PREF_PY4J_ACTIVE));
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.ui.IWorkbenchPreferencePage#init(org.eclipse.ui.IWorkbench)
	 */
	public void init(IWorkbench workbench) {
	}

	protected void updateEnabled(boolean enabled) {
		if (!isControlCreated()) {
			return;
		}
		tcpPort.setEnabled(enabled, getFieldEditorParent());
		callPort.setEnabled(enabled, getFieldEditorParent());
		swt.setEnabled(enabled, getFieldEditorParent());
		info.setEnabled(enabled, getFieldEditorParent());
	}

	public void propertyChange(PropertyChangeEvent event) {
		super.propertyChange(event);

		if (getFieldEditorParent() == null
				|| getFieldEditorParent().isDisposed()) {
			return;
		}

		if (event.getSource() == active) {
			updateEnabled((Boolean) event.getNewValue());
		}

	}

}