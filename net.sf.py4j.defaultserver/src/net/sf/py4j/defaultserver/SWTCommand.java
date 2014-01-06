package net.sf.py4j.defaultserver;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.lang.Thread.State;

import org.eclipse.swt.widgets.Display;

import py4j.Py4JException;
import py4j.commands.CallCommand;
import py4j.commands.Command;

/**
 * Delegates execution of command to swt thread if needed.
 * 
 * @author fcp94556
 * 
 */
public final class SWTCommand extends CallCommand {

	private Command delegate;

	public SWTCommand(Command delegate) {
		this.delegate = delegate;
	}

	/**
	 * Problem is that in pydev, the . operator calls from UI thread into
	 * cpython, this then starts a thread to call back into Java using py4j.
	 * That results in this command being run which blocks when the
	 * Display.getDefault().asyncExec(...) attempts to be called because the SWT
	 * UI thread is already locked. We use isThreadRunnable(...) to try to avoid
	 * this.
	 * 
	 * However this is not a 100% reliable approach because it could be that a
	 * UI call is made here when the UI thread is temporarily blocked. In
	 * practice this is uncommon and non-fatal so give that the SWT ability is
	 * extremely useful we risk it.
	 * 
	 * Text has been added to make it clear that the SWT model works better with
	 * a pure python repl rather than a pydev console.
	 * 
	 * The normal method call from pydev is not in the UI thread and then this
	 * works.
	 */
	@Override
	public void execute(final String commandName, final BufferedReader reader,
			final BufferedWriter writer) throws Py4JException, IOException {

		if (Display.getDefault() == null || Display.getDefault().isDisposed()) {
			delegate.execute(commandName, reader, writer);
			return;
		}

		if (!isThreadRunnable(Display.getDefault().getThread())) {
			delegate.execute(commandName, reader, writer);
			return;
		}
		if (!isThreadRunnable(Display.getDefault().getSyncThread())) {
			delegate.execute(commandName, reader, writer);
			return;
		}

		final DelegateRunnable runner = new DelegateRunnable(commandName,
				reader, writer);
		Display.getDefault().asyncExec(runner);

		int time = 0;
		// We wait for 5s by default for the method to get to the top of the
		// stack and return.
		final int waitTime = Integer.getInteger(
				"net.sf.py4j.defaultserver.waitTime", 5000);
		while (runner.isActive()) {
			try {
				Thread.sleep(100);
				time += 100;
				if (time > waitTime) {
					runner.setActive(false); // It timed out
					Display.getDefault().wake();
					break;
				}

			} catch (InterruptedException e) {
				runner.setActive(false); // It timed out
				Display.getDefault().wake();
				break;
			}
		}
		runner.throwIfRequired();
	}

	/**
	 * If the thread is null, still returns true.
	 * 
	 * @param t
	 * @return true if thread is Runnable or null
	 */
	private boolean isThreadRunnable(Thread t) {
		if (t == null) {
			return true;
		}
		final State state = t.getState();
		return state == State.RUNNABLE;
	}

	protected class DelegateRunnable implements Runnable {

		private String commandName;
		private BufferedReader reader;
		private BufferedWriter writer;
		private boolean active;
		private Exception error;

		DelegateRunnable(final String commandName, final BufferedReader reader,
				final BufferedWriter writer) {
			this.commandName = commandName;
			this.reader = reader;
			this.writer = writer;
			this.active = true;
		}

		public void setActive(boolean b) {
			active = b;
		}

		public void run() {
			try {
				if (!active) {
					return;
				}
				delegate.execute(commandName, reader, writer);
				active = false;
			} catch (Py4JException pe) {
				error = pe;
			} catch (IOException ie) {
				error = ie;
			} catch (Throwable ne) {
				error = new IOException(ne);
			}
		}

		public boolean isActive() {
			return active;
		}

		void throwIfRequired() throws Py4JException, IOException {
			if (error != null) {
				if (error instanceof Py4JException) {
					throw (Py4JException) error;
				}
				if (error instanceof IOException) {
					throw (IOException) error;
				}
			}
		}
	}

}
