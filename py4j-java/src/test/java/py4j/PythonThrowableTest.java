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

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;

import java.io.PrintWriter;
import java.io.StringWriter;

import org.junit.Test;

import py4j.PythonThrowable.PythonStackTraceElement;

public class PythonThrowableTest {

	@Test
	public void testPythonException1() {
		String pythonString = "Traceback (most recent call last):\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1621, in <moduleName>\r\n"
				+ "    main()\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1615, in main\r\n"
				+ "    globals = debugger.run(setup['fileName'], None, None, is_module)\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1022, in run\r\n"
				+ "    pydev_imports.execfile(fileName, globals, locals)  # execute the script\r\n"
				+ "  File \"C:\\Users\\slewis\\git\\Py4j-RemoteServicesProvider\\examples\\org.eclipse.ecf.examples.protobuf.hello\\python-src\\run.py\", line 9, in <moduleName>\r\n"
				+ "    from osgiservicebridge.protobuf import protobuf_remote_service, protobuf_remote_service_method,\\\r\n"
				+ "ImportError: cannot import name PythonServiceExporter";
		int originalLines = pythonString.split("\\n").length;
		StringWriter sw = new StringWriter();
		PythonThrowable pt = new PythonThrowable(pythonString);
		assertNotNull(pt.getMessage());
		assertNull(pt.getCause());
		pt.printStackTrace(new PrintWriter(sw));
		String stackTrace = sw.toString();
		assertNotNull(stackTrace);
		PythonStackTraceElement[] stack = pt.getPythonStackTraceElements();
		// number of lines should be same
		assertEquals(stackTrace.split("\\n").length, originalLines);

		for (PythonStackTraceElement e : stack)
			System.out.println(e.toPythonString());
		System.out.println(stackTrace);
	}

	@Test
	public void testPythonException2() {
		String pythonString = "Traceback (most recent call last):\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1621, in <moduleName>\r\n"
				+ "    main()\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1615, in main\r\n"
				+ "    globals = debugger.run(setup['fileName'], None, None, is_module)\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1022, in run\r\n"
				+ "    pydev_imports.execfile(fileName, globals, locals)  # execute the script\r\n"
				+ "  File \"C:\\Users\\slewis\\git\\Py4j-RemoteServicesProvider\\examples\\org.eclipse.ecf.examples.protobuf.hello\\python-src\\run.py\", line 67, in <moduleName>\r\n"
				+ "    hellomsg = create_hellomsgcontent('saying hello from python to java service')\r\n"
				+ "  File \"C:\\Users\\slewis\\git\\Py4j-RemoteServicesProvider\\examples\\org.eclipse.ecf.examples.protobuf.hello\\python-src\\run.py\", line 25, in create_hellomsgcontent\r\n"
				+ "    tuple()[1]\r\n" + "IndexError: tuple index out of range\r\n" + "";
		int originalLines = pythonString.split("\\n").length;
		StringWriter sw = new StringWriter();
		PythonThrowable pt = new PythonThrowable(pythonString);
		assertNotNull(pt.getMessage());
		assertNull(pt.getCause());
		pt.printStackTrace(new PrintWriter(sw));
		String stackTrace = sw.toString();
		assertNotNull(stackTrace);
		PythonStackTraceElement[] stack = pt.getPythonStackTraceElements();
		// number of lines should be same
		assertEquals(stackTrace.split("\\n").length, originalLines);

		for (PythonStackTraceElement e : stack)
			System.out.println(e.toPythonString());
		System.out.println(stackTrace);
	}

	@Test
	public void testPythonException3() {
		String pythonString = "Traceback (most recent call last):\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1621, in <moduleName>\r\n"
				+ "    main()\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1615, in main\r\n"
				+ "    globals = debugger.run(setup['fileName'], None, None, is_module)\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1022, in run\r\n"
				+ "    pydev_imports.execfile(fileName, globals, locals)  # execute the script\r\n"
				+ "  File \"C:\\Users\\slewis\\git\\Py4j-RemoteServicesProvider\\examples\\org.eclipse.ecf.examples.protobuf.hello\\python-src\\run.py\", line 67, in <moduleName>\r\n"
				+ "    hellomsg = create_hellomsgcontent('saying hello from python to java service')\r\n"
				+ "  File \"C:\\Users\\slewis\\git\\Py4j-RemoteServicesProvider\\examples\\org.eclipse.ecf.examples.protobuf.hello\\python-src\\run.py\", line 25, in create_hellomsgcontent\r\n"
				+ "    tuple()[1]\r\n" + "IndexError: tuple index out of range\r\n" + "";
		int originalLines = pythonString.split("\\n").length;
		StringWriter sw = new StringWriter();
		PythonThrowable pt = new PythonThrowable(pythonString);
		assertNotNull(pt.getMessage());
		assertNull(pt.getCause());
		pt.printStackTrace(new PrintWriter(sw));
		String stackTrace = sw.toString();
		assertNotNull(stackTrace);
		PythonStackTraceElement[] stack = pt.getPythonStackTraceElements();
		// number of lines should be same
		assertEquals(stackTrace.split("\\n").length, originalLines);

		for (PythonStackTraceElement e : stack)
			System.out.println(e.toPythonString());

		System.out.println("---");
		pt.printStackTrace();
	}

	@Test
	public void testPythonException4() {
		String pythonString = "Traceback (most recent call last):\n" + "  File \"<stdin>\", line 20, in <module>\r\n"
				+ "  File \"<stdin>\", line 10, in foo\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1022, in run\r\n"
				+ "    pydev_imports.execfile(fileName, globals, locals)  # execute the script\r\n"
				+ "  File \"C:\\Users\\slewis\\git\\Py4j-RemoteServicesProvider\\examples\\org.eclipse.ecf.examples.protobuf.hello\\python-src\\run.py\", line 67, in <moduleName>\r\n"
				+ "    hellomsg = create_hellomsgcontent('saying hello from python to java service')\r\n"
				+ "  File \"C:\\Users\\slewis\\git\\Py4j-RemoteServicesProvider\\examples\\org.eclipse.ecf.examples.protobuf.hello\\python-src\\run.py\", line 25, in create_hellomsgcontent\r\n"
				+ "    tuple()[1]\r\n" + "IndexError: tuple index out of range\r\n" + "";
		int originalLines = pythonString.split("\\n").length;
		StringWriter sw = new StringWriter();
		PythonThrowable pt = new PythonThrowable(pythonString);
		assertNotNull(pt.getMessage());
		assertNull(pt.getCause());
		pt.printStackTrace(new PrintWriter(sw));
		String stackTrace = sw.toString();
		assertNotNull(stackTrace);
		PythonStackTraceElement[] stack = pt.getPythonStackTraceElements();
		// number of lines should be same
		assertEquals(stackTrace.split("\\n").length, originalLines);

		for (PythonStackTraceElement e : stack)
			System.out.println(e.toPythonString());
		System.out.println(stackTrace);
	}

	@Test
	public void testPythonException5() {
		String pythonString = "Traceback (most recent call last):\r\n" + "  File \"<stdin>\", line 3, in compute\r\n"
				+ "ZeroDivisionError: division by zero\r\n" + "\r\n"
				+ "During handling of the above exception, another exception occurred:\r\n" + "\r\n"
				+ "Traceback (most recent call last):\r\n" + "  File \"<stdin>\", line 1, in <module>\r\n"
				+ "  File \"<stdin>\", line 5, in compute\r\n" + "  File \"<stdin>\", line 2, in log\r\n"
				+ "FileNotFoundError: [Errno 2] No such file or directory: 'logfile.txt'";
		int originalLines = pythonString.split("\\n").length;
		PythonThrowable pt = new PythonThrowable(pythonString);
		assertNotNull(pt.getMessage());
		Throwable c = pt.getCause();
		assertTrue(c instanceof PythonThrowable);
		PythonThrowable cause = (PythonThrowable) c;
		System.out.println("--Cause--");
		cause.printStackTrace();
		System.out.println("--End Cause---");
		StringWriter sw = new StringWriter();
		pt.printStackTrace(new PrintWriter(sw));
		String stackTrace = sw.toString();
		assertNotNull(stackTrace);
		PythonStackTraceElement[] stack = pt.getPythonStackTraceElements();
		// number of lines should be same
		assertEquals(stackTrace.split("\\n").length, originalLines);
		System.out.println("--Stack Trace--");
		for (PythonStackTraceElement e : stack)
			System.out.println(e.toPythonString());
		System.out.println(stackTrace);
		System.out.println("--End Stack Trace--");
		System.out.println("--Full Stack--");
		pt.printStackTrace();
		System.out.println("--End Full Stack---");
	}

	@Test
	public void testPythonException6() {
		String pythonString = "Exception: two\r\n" + "\r\n"
				+ "The above exception was the direct cause of the following exception:\r\n" + "\r\n"
				+ "Traceback (most recent call last):\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1621, in <module>\r\n"
				+ "    main()\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1615, in main\r\n"
				+ "    globals = debugger.run(setup['file'], None, None, is_module)\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1022, in run\r\n"
				+ "    pydev_imports.execfile(file, globals, locals)  # execute the script\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\_pydev_imps\\_pydev_execfile.py\", line 25, in execfile\r\n"
				+ "    exec(compile(contents+\"\\n\", file, 'exec'), glob, loc)\r\n"
				+ "  File \"C:\\Users\\slewis\\git\\Py4j-RemoteServicesProvider\\examples\\org.eclipse.ecf.examples.importhook.main\\src\\run.py\", line 14, in <module>\r\n"
				+ "    raise Exception('one') from Exception('two')\r\n" + "Exception: one";
		int originalLines = pythonString.split("\\n").length;
		PythonThrowable pt = new PythonThrowable(pythonString);
		assertNotNull(pt.getMessage());
		Throwable c = pt.getCause();
		assertTrue(c instanceof PythonThrowable);
		PythonThrowable cause = (PythonThrowable) c;
		System.out.println("--Cause--");
		cause.printStackTrace();
		System.out.println("--End Cause---");
		StringWriter sw = new StringWriter();
		pt.printStackTrace(new PrintWriter(sw));
		String stackTrace = sw.toString();
		assertNotNull(stackTrace);
		PythonStackTraceElement[] stack = pt.getPythonStackTraceElements();
		// number of lines should be same
		assertEquals(stackTrace.split("\\n").length, originalLines);
		System.out.println("--Stack Trace--");
		for (PythonStackTraceElement e : stack)
			System.out.println(e.toPythonString());
		System.out.println(stackTrace);
		System.out.println("--End Stack Trace--");
		System.out.println("--Full Stack--");
		pt.printStackTrace();
		System.out.println("--End Full Stack---");
	}

	@Test
	public void testPythonException7() {
		String pythonString = "Exception\r\n" + "\r\n"
				+ "The above exception was the direct cause of the following exception:\r\n" + "\r\n"
				+ "Traceback (most recent call last):\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1621, in <module>\r\n"
				+ "    main()\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1615, in main\r\n"
				+ "    globals = debugger.run(setup['file'], None, None, is_module)\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1022, in run\r\n"
				+ "    pydev_imports.execfile(file, globals, locals)  # execute the script\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\_pydev_imps\\_pydev_execfile.py\", line 25, in execfile\r\n"
				+ "    exec(compile(contents+\"\\n\", file, 'exec'), glob, loc)\r\n"
				+ "  File \"C:\\Users\\slewis\\git\\Py4j-RemoteServicesProvider\\examples\\org.eclipse.ecf.examples.importhook.main\\src\\run.py\", line 14, in <module>\r\n"
				+ "    raise Exception from Exception\r\n" + "Exception";
		int originalLines = pythonString.split("\\n").length;
		PythonThrowable pt = new PythonThrowable(pythonString);
		assertNotNull(pt.getMessage());
		Throwable c = pt.getCause();
		assertTrue(c instanceof PythonThrowable);
		PythonThrowable cause = (PythonThrowable) c;
		System.out.println("--Cause--");
		cause.printStackTrace();
		System.out.println("--End Cause---");
		StringWriter sw = new StringWriter();
		pt.printStackTrace(new PrintWriter(sw));
		String stackTrace = sw.toString();
		assertNotNull(stackTrace);
		PythonStackTraceElement[] stack = pt.getPythonStackTraceElements();
		// number of lines should be same
		assertEquals(stackTrace.split("\\n").length, originalLines);
		System.out.println("--Stack Trace--");
		for (PythonStackTraceElement e : stack)
			System.out.println(e.toPythonString());
		System.out.println(stackTrace);
		System.out.println("--End Stack Trace--");
		System.out.println("--Full Stack--");
		pt.printStackTrace();
		System.out.println("--End Full Stack---");
	}

	@Test
	public void testPythonException8() {
		String pythonString = "Traceback (most recent call last):\r\n"
				+ "  File \"C:\\Users\\slewis\\git\\Py4j-RemoteServicesProvider\\examples\\org.eclipse.ecf.examples.importhook.main\\src\\a.py\", line 14, in run\r\n"
				+ "    b.run()\r\n"
				+ "  File \"C:\\Users\\slewis\\git\\Py4j-RemoteServicesProvider\\examples\\org.eclipse.ecf.examples.importhook.main\\src\\b.py\", line 9, in run\r\n"
				+ "    1 / 0\r\n" + "ZeroDivisionError: division by zero\r\n" + "\r\n"
				+ "The above exception was the direct cause of the following exception:\r\n" + "\r\n"
				+ "Traceback (most recent call last):\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1621, in <module>\r\n"
				+ "    main()\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1615, in main\r\n"
				+ "    globals = debugger.run(setup['file'], None, None, is_module)\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1022, in run\r\n"
				+ "    pydev_imports.execfile(file, globals, locals)  # execute the script\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\_pydev_imps\\_pydev_execfile.py\", line 25, in execfile\r\n"
				+ "    exec(compile(contents+\"\\n\", file, 'exec'), glob, loc)\r\n"
				+ "  File \"C:\\Users\\slewis\\git\\Py4j-RemoteServicesProvider\\examples\\org.eclipse.ecf.examples.importhook.main\\src\\run.py\", line 18, in <module>\r\n"
				+ "    a.run()\r\n"
				+ "  File \"C:\\Users\\slewis\\git\\Py4j-RemoteServicesProvider\\examples\\org.eclipse.ecf.examples.importhook.main\\src\\a.py\", line 16, in run\r\n"
				+ "    raise Exception('exeception in class A') from exc\r\n" + "Exception: exeception in class A";
		int originalLines = pythonString.split("\\n").length;
		PythonThrowable pt = new PythonThrowable(pythonString);
		assertNotNull(pt.getMessage());
		Throwable c = pt.getCause();
		assertTrue(c instanceof PythonThrowable);
		PythonThrowable cause = (PythonThrowable) c;
		System.out.println("--Cause--");
		cause.printStackTrace();
		System.out.println("--End Cause---");
		StringWriter sw = new StringWriter();
		pt.printStackTrace(new PrintWriter(sw));
		String stackTrace = sw.toString();
		assertNotNull(stackTrace);
		PythonStackTraceElement[] stack = pt.getPythonStackTraceElements();
		// number of lines should be same
		assertEquals(stackTrace.split("\\n").length, originalLines);
		System.out.println("--Stack Trace--");
		for (PythonStackTraceElement e : stack)
			System.out.println(e.toPythonString());
		System.out.println(stackTrace);
		System.out.println("--End Stack Trace--");
		System.out.println("--Full Stack--");
		pt.printStackTrace();
		System.out.println("--End Full Stack---");
	}

	@Test
	public void testPythonExceptionJava1() {
		String pythonString = "Traceback (most recent call last):\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1621, in <moduleName>\r\n"
				+ "    main()\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1615, in main\r\n"
				+ "    globals = debugger.run(setup['fileName'], None, None, is_module)\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1022, in run\r\n"
				+ "    pydev_imports.execfile(fileName, globals, locals)  # execute the script\r\n"
				+ "  File \"C:\\Users\\slewis\\git\\Py4j-RemoteServicesProvider\\examples\\org.eclipse.ecf.examples.protobuf.hello\\python-src\\run.py\", line 9, in <moduleName>\r\n"
				+ "    from osgiservicebridge.protobuf import protobuf_remote_service, protobuf_remote_service_method,\\\r\n"
				+ "ImportError: cannot import name PythonServiceExporter";
		StringWriter sw = new StringWriter();
		PythonThrowable pt = new PythonThrowable(pythonString, true);
		assertNotNull(pt.getMessage());
		assertNull(pt.getCause());
		pt.printStackTrace(new PrintWriter(sw));
		assertNotNull(sw.toString());
		PythonStackTraceElement[] stack = pt.getPythonStackTraceElements();

		for (PythonStackTraceElement e : stack)
			System.out.println(e.toJavaString());
		System.out.println(sw.toString());
	}

	@Test
	public void testPythonExceptionJava2() {
		String pythonString = "Traceback (most recent call last):\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1621, in <moduleName>\r\n"
				+ "    main()\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1615, in main\r\n"
				+ "    globals = debugger.run(setup['fileName'], None, None, is_module)\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1022, in run\r\n"
				+ "    pydev_imports.execfile(fileName, globals, locals)  # execute the script\r\n"
				+ "  File \"C:\\Users\\slewis\\git\\Py4j-RemoteServicesProvider\\examples\\org.eclipse.ecf.examples.protobuf.hello\\python-src\\run.py\", line 67, in <moduleName>\r\n"
				+ "    hellomsg = create_hellomsgcontent('saying hello from python to java service')\r\n"
				+ "  File \"C:\\Users\\slewis\\git\\Py4j-RemoteServicesProvider\\examples\\org.eclipse.ecf.examples.protobuf.hello\\python-src\\run.py\", line 25, in create_hellomsgcontent\r\n"
				+ "    tuple()[1]\r\n" + "IndexError: tuple index out of range\r\n" + "";
		StringWriter sw = new StringWriter();
		PythonThrowable pt = new PythonThrowable(pythonString, true);
		assertNotNull(pt.getMessage());
		assertNull(pt.getCause());
		pt.printStackTrace(new PrintWriter(sw));
		assertNotNull(sw.toString());
		PythonStackTraceElement[] stack = pt.getPythonStackTraceElements();

		for (PythonStackTraceElement e : stack)
			System.out.println(e.toJavaString());
		System.out.println(sw.toString());
	}

	@Test
	public void testPythonExceptionJava3() {
		String pythonString = "Traceback (most recent call last):\n" + "  File \"<stdin>\", line 20, in <module>\r\n"
				+ "  File \"<stdin>\", line 10, in foo\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1022, in run\r\n"
				+ "    pydev_imports.execfile(fileName, globals, locals)  # execute the script\r\n"
				+ "  File \"C:\\Users\\slewis\\git\\Py4j-RemoteServicesProvider\\examples\\org.eclipse.ecf.examples.protobuf.hello\\python-src\\run.py\", line 67, in <moduleName>\r\n"
				+ "    hellomsg = create_hellomsgcontent('saying hello from python to java service')\r\n"
				+ "  File \"C:\\Users\\slewis\\git\\Py4j-RemoteServicesProvider\\examples\\org.eclipse.ecf.examples.protobuf.hello\\python-src\\run.py\", line 25, in create_hellomsgcontent\r\n"
				+ "    tuple()[1]\r\n" + "IndexError: tuple index out of range\r\n" + "";
		StringWriter sw = new StringWriter();
		PythonThrowable pt = new PythonThrowable(pythonString, true);
		assertNotNull(pt.getMessage());
		assertNull(pt.getCause());
		pt.printStackTrace(new PrintWriter(sw));
		assertNotNull(sw.toString());
		PythonStackTraceElement[] stack = pt.getPythonStackTraceElements();

		for (PythonStackTraceElement e : stack)
			System.out.println(e.toJavaString());
		System.out.println(sw.toString());
	}

	@Test
	public void testJavaException4() {
		String pythonString = "Traceback (most recent call last):\n" + "  File \"<stdin>\", line 20, in <module>\r\n"
				+ "  File \"<stdin>\", line 10, in foo\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1022, in run\r\n"
				+ "    pydev_imports.execfile(fileName, globals, locals)  # execute the script\r\n"
				+ "  File \"C:\\Users\\slewis\\git\\Py4j-RemoteServicesProvider\\examples\\org.eclipse.ecf.examples.protobuf.hello\\python-src\\run.py\", line 67, in <moduleName>\r\n"
				+ "    hellomsg = create_hellomsgcontent('saying hello from python to java service')\r\n"
				+ "  File \"C:\\Users\\slewis\\git\\Py4j-RemoteServicesProvider\\examples\\org.eclipse.ecf.examples.protobuf.hello\\python-src\\run.py\", line 25, in create_hellomsgcontent\r\n"
				+ "    tuple()[1]\r\n" + "IndexError: tuple index out of range\r\n" + "";
		StringWriter sw = new StringWriter();
		PythonThrowable pt = new PythonThrowable(pythonString);
		assertNotNull(pt.getMessage());
		assertNull(pt.getCause());
		pt.printStackTrace(new PrintWriter(sw));
		String stackTrace = sw.toString();
		assertNotNull(stackTrace);
		PythonStackTraceElement[] stack = pt.getPythonStackTraceElements();

		for (PythonStackTraceElement e : stack)
			System.out.println(e.toPythonString());
		System.out.println(stackTrace);
	}

	@Test
	public void testPythonExceptionJava5() {
		String pythonString = "Traceback (most recent call last):\r\n" + "  File \"<stdin>\", line 3, in compute\r\n"
				+ "ZeroDivisionError: division by zero\r\n" + "\r\n"
				+ "During handling of the above exception, another exception occurred:\r\n" + "\r\n"
				+ "Traceback (most recent call last):\r\n" + "  File \"<stdin>\", line 1, in <module>\r\n"
				+ "  File \"<stdin>\", line 5, in compute\r\n" + "  File \"<stdin>\", line 2, in log\r\n"
				+ "FileNotFoundError: [Errno 2] No such file or directory: 'logfile.txt'";
		PythonThrowable pt = new PythonThrowable(pythonString);
		assertNotNull(pt.getMessage());
		Throwable c = pt.getCause();
		assertTrue(c instanceof PythonThrowable);
		PythonThrowable cause = (PythonThrowable) c;
		System.out.println("--Cause--");
		cause.printStackTraceJava();
		System.out.println("--End Cause---");
		StringWriter sw = new StringWriter();
		pt.printStackTraceJava(new PrintWriter(sw));
		String stackTrace = sw.toString();
		assertNotNull(stackTrace);
		PythonStackTraceElement[] stack = pt.getPythonStackTraceElements();
		System.out.println("--Stack Trace--");
		for (PythonStackTraceElement e : stack)
			System.out.println(e.toJavaString());
		System.out.println(stackTrace);
		System.out.println("--End Stack Trace--");
		System.out.println("--Full Stack--");
		pt.printStackTraceJava();
		System.out.println("--End Full Stack---");
	}

	@Test
	public void testPythonExceptionJava6() {
		String pythonString = "Exception: two\r\n" + "\r\n"
				+ "The above exception was the direct cause of the following exception:\r\n" + "\r\n"
				+ "Traceback (most recent call last):\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1621, in <module>\r\n"
				+ "    main()\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1615, in main\r\n"
				+ "    globals = debugger.run(setup['file'], None, None, is_module)\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1022, in run\r\n"
				+ "    pydev_imports.execfile(file, globals, locals)  # execute the script\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\_pydev_imps\\_pydev_execfile.py\", line 25, in execfile\r\n"
				+ "    exec(compile(contents+\"\\n\", file, 'exec'), glob, loc)\r\n"
				+ "  File \"C:\\Users\\slewis\\git\\Py4j-RemoteServicesProvider\\examples\\org.eclipse.ecf.examples.importhook.main\\src\\run.py\", line 14, in <module>\r\n"
				+ "    raise Exception('one') from Exception('two')\r\n" + "Exception: one";
		PythonThrowable pt = new PythonThrowable(pythonString);
		assertNotNull(pt.getMessage());
		Throwable c = pt.getCause();
		assertTrue(c instanceof PythonThrowable);
		PythonThrowable cause = (PythonThrowable) c;
		System.out.println("--Cause--");
		cause.printStackTraceJava();
		System.out.println("--End Cause---");
		StringWriter sw = new StringWriter();
		pt.printStackTraceJava(new PrintWriter(sw));
		String stackTrace = sw.toString();
		assertNotNull(stackTrace);
		PythonStackTraceElement[] stack = pt.getPythonStackTraceElements();
		System.out.println("--Stack Trace--");
		for (PythonStackTraceElement e : stack)
			System.out.println(e.toJavaString());
		System.out.println(stackTrace);
		System.out.println("--End Stack Trace--");
		System.out.println("--Full Stack--");
		pt.printStackTraceJava();
		System.out.println("--End Full Stack---");
	}

	@Test
	public void testPythonExceptionJava7() {
		String pythonString = "Exception\r\n" + "\r\n"
				+ "The above exception was the direct cause of the following exception:\r\n" + "\r\n"
				+ "Traceback (most recent call last):\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1621, in <module>\r\n"
				+ "    main()\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1615, in main\r\n"
				+ "    globals = debugger.run(setup['file'], None, None, is_module)\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1022, in run\r\n"
				+ "    pydev_imports.execfile(file, globals, locals)  # execute the script\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\_pydev_imps\\_pydev_execfile.py\", line 25, in execfile\r\n"
				+ "    exec(compile(contents+\"\\n\", file, 'exec'), glob, loc)\r\n"
				+ "  File \"C:\\Users\\slewis\\git\\Py4j-RemoteServicesProvider\\examples\\org.eclipse.ecf.examples.importhook.main\\src\\run.py\", line 14, in <module>\r\n"
				+ "    raise Exception from Exception\r\n" + "Exception";
		PythonThrowable pt = new PythonThrowable(pythonString);
		assertNotNull(pt.getMessage());
		Throwable c = pt.getCause();
		assertTrue(c instanceof PythonThrowable);
		PythonThrowable cause = (PythonThrowable) c;
		System.out.println("--Cause--");
		cause.printStackTraceJava();
		System.out.println("--End Cause---");
		StringWriter sw = new StringWriter();
		pt.printStackTraceJava(new PrintWriter(sw));
		String stackTrace = sw.toString();
		assertNotNull(stackTrace);
		PythonStackTraceElement[] stack = pt.getPythonStackTraceElements();
		System.out.println("--Stack Trace--");
		for (PythonStackTraceElement e : stack)
			System.out.println(e.toJavaString());
		System.out.println(stackTrace);
		System.out.println("--End Stack Trace--");
		System.out.println("--Full Stack--");
		pt.printStackTraceJava();
		System.out.println("--End Full Stack---");
	}

	@Test
	public void testPythonExceptionJava8() {
		String pythonString = "Traceback (most recent call last):\r\n"
				+ "  File \"C:\\Users\\slewis\\git\\Py4j-RemoteServicesProvider\\examples\\org.eclipse.ecf.examples.importhook.main\\src\\a.py\", line 14, in run\r\n"
				+ "    b.run()\r\n"
				+ "  File \"C:\\Users\\slewis\\git\\Py4j-RemoteServicesProvider\\examples\\org.eclipse.ecf.examples.importhook.main\\src\\b.py\", line 9, in run\r\n"
				+ "    1 / 0\r\n" + "ZeroDivisionError: division by zero\r\n" + "\r\n"
				+ "The above exception was the direct cause of the following exception:\r\n" + "\r\n"
				+ "Traceback (most recent call last):\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1621, in <module>\r\n"
				+ "    main()\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1615, in main\r\n"
				+ "    globals = debugger.run(setup['file'], None, None, is_module)\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\pydevd.py\", line 1022, in run\r\n"
				+ "    pydev_imports.execfile(file, globals, locals)  # execute the script\r\n"
				+ "  File \"C:\\eclipse.oxygen.2\\eclipse\\plugins\\org.python.pydev_6.2.0.201711281614\\pysrc\\_pydev_imps\\_pydev_execfile.py\", line 25, in execfile\r\n"
				+ "    exec(compile(contents+\"\\n\", file, 'exec'), glob, loc)\r\n"
				+ "  File \"C:\\Users\\slewis\\git\\Py4j-RemoteServicesProvider\\examples\\org.eclipse.ecf.examples.importhook.main\\src\\run.py\", line 18, in <module>\r\n"
				+ "    a.run()\r\n"
				+ "  File \"C:\\Users\\slewis\\git\\Py4j-RemoteServicesProvider\\examples\\org.eclipse.ecf.examples.importhook.main\\src\\a.py\", line 16, in run\r\n"
				+ "    raise Exception('exeception in class A') from exc\r\n" + "Exception: exeception in class A";
		PythonThrowable pt = new PythonThrowable(pythonString);
		assertNotNull(pt.getMessage());
		Throwable c = pt.getCause();
		assertTrue(c instanceof PythonThrowable);
		PythonThrowable cause = (PythonThrowable) c;
		System.out.println("--Cause--");
		cause.printStackTraceJava();
		System.out.println("--End Cause---");
		StringWriter sw = new StringWriter();
		pt.printStackTraceJava(new PrintWriter(sw));
		String stackTrace = sw.toString();
		assertNotNull(stackTrace);
		PythonStackTraceElement[] stack = pt.getPythonStackTraceElements();
		System.out.println("--Stack Trace--");
		for (PythonStackTraceElement e : stack)
			System.out.println(e.toJavaString());
		System.out.println(stackTrace);
		System.out.println("--End Stack Trace--");
		System.out.println("--Full Stack--");
		pt.printStackTraceJava();
		System.out.println("--End Full Stack---");
	}

}
