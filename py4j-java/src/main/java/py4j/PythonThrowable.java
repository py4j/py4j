/******************************************************************************
 * Copyright (c) 2009-2016, Barthelemy Dagenais and individual contributors.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * - Redistributions of source code must retain the above copyright notice,
 * this list of conditions and the following disclaimer.
 *
 * - Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 *
 * - The name of the author may not be used to endorse or promote products
 * derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 *****************************************************************************/
package py4j;

import java.io.PrintStream;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.util.ArrayList;
import java.util.List;

/**
 * Class to represent a Python Exceptions. Parses the String returned from traceback.format_exc() and prints it in
 * Python form or Java form. Both of these forms can be accessed via printStackTracePython(...) or
 * printStackTraceJava(...). The form returned by the inherited printStackTrace(...) methods can also be set by
 * explicitly using this constructor:
 * 
 * public PythonThrowable(String pythonErrorString, boolean useJavaStackFormat)
 * 
 */
public class PythonThrowable extends Throwable {

	private static String NEWLINE = System.getProperty("line.separator");
	private static final String FILE_PREFIX = "  File \"";
	private static final String PYTHON_FIRST_LINE = "Traceback (most recent call last):";

	private static final long serialVersionUID = -1622656943236338778L;

	private abstract static class PrintStreamOrWriter {
		abstract Object lock();

		abstract void println(Object o);
	}

	private static class WrappedPrintStream extends PrintStreamOrWriter {
		private final PrintStream printStream;

		WrappedPrintStream(PrintStream printStream) {
			this.printStream = printStream;
		}

		Object lock() {
			return printStream;
		}

		void println(Object o) {
			printStream.println(o);
		}
	}

	private static class WrappedPrintWriter extends PrintStreamOrWriter {
		private final PrintWriter printWriter;

		WrappedPrintWriter(PrintWriter printWriter) {
			this.printWriter = printWriter;
		}

		Object lock() {
			return printWriter;
		}

		void println(Object o) {
			printWriter.println(o);
		}
	}

	public static class PythonStackTraceElement {
		private static final String LINENO_PREFIX = " line ";
		private static final String MOD_PREFIX = " in ";
		private static final String JAVA_FILE_PREFIX = "        at ";
		private static final String JAVA_CODE_PREFIX = "            ";

		private String fileName;
		private int line;
		private String moduleName;
		private String codeLine;

		public PythonStackTraceElement(String fileLine, String codeLine) {
			String[] fileLineParts = fileLine.split(",");
			if (fileLineParts.length >= 3) {
				this.fileName = fileLineParts[0].substring(FILE_PREFIX.length(), fileLineParts[0].length() - 1).trim();
				try {
					this.line = Integer.parseInt(fileLineParts[1].substring(LINENO_PREFIX.length()).trim());
				} catch (NumberFormatException e) {
					// should not happen
					throw new RuntimeException("Cannot parse line number from fileLine=" + fileLine);
				}
				this.moduleName = fileLineParts[2].substring(MOD_PREFIX.length()).trim();
			}
			if (codeLine != null)
				this.codeLine = codeLine.trim();
		}

		public String getFilename() {
			return this.fileName;
		}

		public int getLine() {
			return this.line;
		}

		public String getModuleName() {
			return this.moduleName;
		}

		public String getCodeLine() {
			return this.codeLine;
		}

		public String toPythonString() {
			StringWriter sw = new StringWriter();
			WrappedPrintWriter pw = new WrappedPrintWriter(new PrintWriter(sw));
			writePythonFileLine(pw);
			writePythonCodeLine(pw);
			return sw.toString();
		}

		public String toJavaString() {
			StringWriter sw = new StringWriter();
			WrappedPrintWriter pw = new WrappedPrintWriter(new PrintWriter(sw));
			writeJavaFileLine(pw);
			writeJavaCodeLine(pw);
			return sw.toString();
		}

		void writeJavaCodeLine(PrintStreamOrWriter ps) {
			if (this.codeLine != null)
				ps.println(JAVA_CODE_PREFIX + this.codeLine);
		}

		void writeJavaFileLine(PrintStreamOrWriter ps) {
			StringBuffer buf = new StringBuffer(JAVA_FILE_PREFIX);
			buf.append(this.fileName).append(":").append(this.line).append(" ").append(this.moduleName);
			ps.println(buf.toString());
		}

		void writePythonFileLine(PrintStreamOrWriter ps) {
			StringBuffer buf = new StringBuffer(FILE_PREFIX);
			buf.append(this.fileName).append("\"").append(",");
			buf.append(LINENO_PREFIX).append(this.line).append(",");
			buf.append(MOD_PREFIX).append(this.moduleName);
			ps.println(buf.toString());
		}

		void writePythonCodeLine(PrintStreamOrWriter ps) {
			if (this.codeLine != null)
				ps.println("    " + this.codeLine);
		}

		public String toString() {
			return toPythonString();
		}
	}

	private final String pythonExceptionType;
	private final String pythonExceptionMsg;
	private PythonStackTraceElement[] stackTraceElements;
	private final boolean useJavaStackFormat;
	private final String pythonCauseMessage;

	public PythonStackTraceElement[] getPythonStackTraceElements() {
		return stackTraceElements.clone();
	}

	public static String[] parseExceptionLine(String exceptionLine) {
		String[] result = new String[2];
		result[0] = "Exception";
		result[1] = "";
		String[] parsedLastLine = exceptionLine.split(":");
		if (parsedLastLine.length >= 2) {
			result[0] = parsedLastLine[0];
			result[1] = parsedLastLine[1];
		} else if (parsedLastLine.length > 0)
			result[1] = parsedLastLine[0];
		return result;
	}

	public static void parsePythonStackTrace(PythonThrowable t, String[] stackLines) {
		int firstTraceback = -1;
		// Find first occurrence of line with 'Traceback (most recent call first):'
		for (int index = stackLines.length - 1; index >= 0; index--) {
			if (stackLines[index].startsWith(PYTHON_FIRST_LINE)) {
				firstTraceback = index;
				break;
			}
		}
		// If not found, we don't have a valid stack trace
		if (firstTraceback < 0)
			throw new NullPointerException("Python stack trace not formatted correctly");
		String[] ourStackLines = null;
		// If the first traceback is > 0, it means we have a chained exception
		if (firstTraceback > 0) {
			// Get the description of the type of chained exception
			// see https://www.python.org/dev/peps/pep-3134/#id30
			ourStackLines = new String[stackLines.length - firstTraceback - 1];
			System.arraycopy(stackLines, firstTraceback + 1, ourStackLines, 0, stackLines.length - firstTraceback - 1);
			// Then create a cause exception if possible
			String msgLine = stackLines[firstTraceback - 2];
			int causeLinesLength = firstTraceback - 3;
			String[] causeLines = new String[causeLinesLength];
			System.arraycopy(stackLines, 0, causeLines, 0, causeLinesLength);
			StringBuffer buf = new StringBuffer();
			for (int i = 0; i < causeLines.length; i++) {
				buf.append(causeLines[i]);
				if (i + 1 < causeLines.length)
					buf.append(NEWLINE);
			}
			// Create new PythonThrowable and set as cause
			t.initCause(new PythonThrowable(msgLine, buf.toString(), t.useJavaStackFormat));
		} else {
			// No chained exceptions so we
			ourStackLines = new String[stackLines.length - 1];
			// take off top line i.e. PYTHON_FIRST_LINE
			System.arraycopy(stackLines, 1, ourStackLines, 0, stackLines.length - 1);
		}
		// Then we process our stack
		List<PythonStackTraceElement> results = new ArrayList<PythonStackTraceElement>();
		for (int index = 0; index < ourStackLines.length;) {
			String fileLine = ourStackLines[index];
			String codeLine = null;
			if (index + 1 < ourStackLines.length && !ourStackLines[index + 1].startsWith(FILE_PREFIX)) {
				codeLine = ourStackLines[index + 1];
				index += 2;
			} else
				index += 1;
			results.add(new PythonStackTraceElement(fileLine, codeLine));
		}
		// Set stack trace elements
		t.stackTraceElements = results.toArray(new PythonStackTraceElement[results.size()]);
	}

	protected PythonThrowable(String pythonCauseMessage, String pythonErrorString, boolean useJavaStackFormat) {
		if (pythonErrorString == null)
			throw new NullPointerException("pythonErrorString must not be null");
		this.pythonCauseMessage = (pythonCauseMessage != null) ? pythonCauseMessage.trim() : null;
		String[] lines = pythonErrorString.split("\\n");
		this.useJavaStackFormat = useJavaStackFormat;
		if (lines.length > 0) {
			String lastLine = lines[lines.length - 1];
			String[] parsedLastLine = parseExceptionLine(lastLine);
			this.pythonExceptionType = parsedLastLine[0].trim();
			this.pythonExceptionMsg = parsedLastLine[1].trim();
			if (lines.length > 1) {
				String[] stackLines = new String[lines.length - 1];
				System.arraycopy(lines, 0, stackLines, 0, lines.length - 1);
				parsePythonStackTrace(this, stackLines);
			} else
				this.stackTraceElements = null;
		} else {
			this.pythonExceptionType = null;
			this.pythonExceptionMsg = null;
			this.stackTraceElements = null;
		}
	}

	public PythonThrowable(String pythonErrorString, boolean useJavaStackFormat) {
		this(null, pythonErrorString, useJavaStackFormat);
	}

	public PythonThrowable(String pythonErrorString) {
		this(pythonErrorString, false);
	}

	public void printStackTrace() {
		printStackTrace(System.err);
	}

	public void printStackTrace(PrintStream s) {
		printStackTrace(new WrappedPrintStream(s));
	}

	public void printStackTrace(PrintWriter s) {
		printStackTrace(new WrappedPrintWriter(s));
	}

	public String getMessage() {
		return this.pythonExceptionMsg;
	}

	public String getExceptionType() {
		return this.pythonExceptionType;
	}

	public boolean useJavaStackFormat() {
		return this.useJavaStackFormat;
	}

	private void printStackTracePython(PrintStreamOrWriter s) {
		synchronized (s.lock()) {
			Throwable t = getCause();
			if (t != null && t.getClass().isAssignableFrom(PythonThrowable.class)) {
				PythonThrowable tc = (PythonThrowable) t;
				tc.printStackTracePython(s);
				s.println("");
				s.println(tc.pythonCauseMessage);
				s.println("");
			}
			s.println(PYTHON_FIRST_LINE);
			if (this.stackTraceElements != null)
				for (PythonStackTraceElement pste : this.stackTraceElements) {
					pste.writePythonFileLine(s);
					pste.writePythonCodeLine(s);
				}
			s.println(this.pythonExceptionType + ": " + this.pythonExceptionMsg);
		}
	}

	public void printStackTraceJava(PrintStream s) {
		printStackTraceJava(false, new WrappedPrintStream(s));
	}

	public void printStackTraceJava(PrintWriter w) {
		printStackTraceJava(false, new WrappedPrintWriter(w));
	}

	public void printStackTraceJava() {
		printStackTraceJava(System.out);
	}

	private void printStackTraceJava(boolean cause, PrintStreamOrWriter s) {
		synchronized (s.lock()) {
			StringBuffer buf = new StringBuffer();
			if (cause)
				buf.append("Caused By: ");
			buf.append("Python exception - ").append(this.pythonExceptionType).append(": ")
					.append(this.pythonExceptionMsg);
			s.println(buf.toString());
			if (this.stackTraceElements != null)
				for (int i = this.stackTraceElements.length - 1; i >= 0; i--) {
					this.stackTraceElements[i].writeJavaFileLine(s);
					this.stackTraceElements[i].writeJavaCodeLine(s);
				}
			Throwable t = getCause();
			if (t != null && t.getClass().isAssignableFrom(PythonThrowable.class)) {
				PythonThrowable c = (PythonThrowable) t;
				c.printStackTraceJava(true, s);
			}
		}
	}

	public void printStackTracePython(PrintStream ps) {
		printStackTracePython(new WrappedPrintStream(ps));
	}

	public void printStackTracePython(PrintWriter pw) {
		printStackTracePython(new WrappedPrintWriter(pw));
	}

	private void printStackTrace(PrintStreamOrWriter s) {
		if (this.useJavaStackFormat)
			printStackTraceJava(false, s);
		else
			printStackTracePython(s);
	}
}
