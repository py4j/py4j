/******************************************************************************
 * Copyright (c) 2009-2018, Barthelemy Dagenais and individual contributors.
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
package py4j.examples;

import java.util.concurrent.BlockingQueue;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.FutureTask;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.logging.ConsoleHandler;
import java.util.logging.Level;
import java.util.logging.Logger;

import javax.net.ServerSocketFactory;
import javax.net.SocketFactory;

import py4j.ClientServer;
import py4j.GatewayServer;

public class MultiClientServer {

	/**
	 * This Runnable for a Thread is designed to simulate the shared nature of a
	 * thread like the UI thread in an SWT application.
	 */
	public static class SharedRunnable implements Runnable {
		private BlockingQueue<FutureTask<?>> queue = new LinkedBlockingQueue<FutureTask<?>>();

		public void add(FutureTask<?> future) throws InterruptedException {
			queue.put(future);
		}

		@Override
		public void run() {
			while (true) {
				try {
					queue.take().run();
				} catch (InterruptedException e) {
					break;
				}
			}
		}
	}

	public static class EntryPoint {
		private SharedRunnable sharedRunnable;
		private int entryId;
		private MultiClientServerGetThreadId pythonGetThreadId;

		public EntryPoint(int entryId, SharedRunnable sharedRunnable) {
			this.entryId = entryId;
			this.sharedRunnable = sharedRunnable;
		}

		public void setPythonThreadIdGetter(MultiClientServerGetThreadId pythonGetThreadId) {
			this.pythonGetThreadId = pythonGetThreadId;
		}

		public int getEntryId() {
			return entryId;
		}

		public long getJavaThreadId() {
			return Thread.currentThread().getId();
		}

		public long getSharedJavaThreadId() throws InterruptedException, ExecutionException {
			FutureTask<Long> futureTask = new FutureTask<Long>(new Callable<Long>() {

				@Override
				public Long call() throws Exception {
					return Thread.currentThread().getId();

				}
			});
			sharedRunnable.add(futureTask);
			return futureTask.get();
		}

		public long getPythonThreadId() {
			return Long.parseLong(pythonGetThreadId.getThreadId());
		}

		public long getSharedPythonThreadId() throws Exception {
			FutureTask<Long> futureTask = new FutureTask<Long>(new Callable<Long>() {

				@Override
				public Long call() throws Exception {
					return Long.parseLong(pythonGetThreadId.getThreadId());
				}
			});
			sharedRunnable.add(futureTask);
			return futureTask.get();
		}

		public long getViaPythonJavaThreadId() {
			return Long.parseLong(pythonGetThreadId.getJavaThreadId());
		}

		public long getSharedViaPythonJavaThreadId() throws Exception {
			FutureTask<Long> futureTask = new FutureTask<Long>(new Callable<Long>() {

				@Override
				public Long call() throws Exception {
					return Long.parseLong(pythonGetThreadId.getJavaThreadId());
				}
			});
			sharedRunnable.add(futureTask);
			return futureTask.get();
		}

	}

	public static void main(String[] args) {
		//		GatewayServer.turnAllLoggingOn();
		Logger logger = Logger.getLogger("py4j");
		logger.setLevel(Level.ALL);
		ConsoleHandler handler = new ConsoleHandler();
		handler.setLevel(Level.FINEST);
		logger.addHandler(handler);
		System.out.println("Starting");

		SharedRunnable sharedRunnable = new SharedRunnable();
		Thread thread = new Thread(sharedRunnable, "SharedRunnable");
		thread.setDaemon(true);
		thread.start();

		EntryPoint entryPoint0 = new EntryPoint(0, sharedRunnable);
		ClientServer clientServer0 = new ClientServer(entryPoint0);
		// Wait for Python side to shut down Java side
		clientServer0.startServer(true);

		// TODO: Refactor with Py4J Pull 204
		// Start the second client server on default + 10 port, the rest of the
		// arguments are the same
		EntryPoint entryPoint1 = new EntryPoint(1, sharedRunnable);
		ClientServer clientServer1 = new ClientServer(GatewayServer.DEFAULT_PORT + 2, GatewayServer.defaultAddress(),
				GatewayServer.DEFAULT_PYTHON_PORT + 2, GatewayServer.defaultAddress(),
				GatewayServer.DEFAULT_CONNECT_TIMEOUT, GatewayServer.DEFAULT_READ_TIMEOUT,
				ServerSocketFactory.getDefault(), SocketFactory.getDefault(), entryPoint1);
		// Wait for Python side to shut down Java side
		clientServer1.startServer(true);

		// Shut down after 5 seconds
		// clientServer.startServer(true);
		// try {
		// Thread.currentThread().sleep(5000);
		// } catch (Exception e) {
		// e.printStackTrace();
		// }
		// clientServer.shutdown();
		//
		// System.out.println("Stopping");
	}
}
