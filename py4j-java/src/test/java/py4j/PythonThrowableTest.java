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

import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertNull;

import java.io.PrintWriter;
import java.io.StringWriter;

import org.junit.Test;

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

		StringWriter sw = new StringWriter();
		PythonThrowable pt = new PythonThrowable(pythonString);
		assertNotNull(pt.getMessage());
		assertNull(pt.getCause());
		pt.printStackTrace(new PrintWriter(sw));
		assertNotNull(sw.toString());
		System.out.println(sw.toString());
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

		StringWriter sw = new StringWriter();
		PythonThrowable pt = new PythonThrowable(pythonString);
		assertNotNull(pt.getMessage());
		assertNull(pt.getCause());
		pt.printStackTrace(new PrintWriter(sw));
		assertNotNull(sw.toString());
		System.out.println(sw.toString());
	}

	@Test
	public void testPythonException3() {
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
		assertNotNull(sw.toString());
		System.out.println(sw.toString());
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
		System.out.println(sw.toString());
	}

}
