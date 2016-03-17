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

import java.io.IOException;
import java.net.InetAddress;
import java.net.Socket;
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;
import java.util.logging.Level;
import java.util.logging.Logger;

import javax.net.SocketFactory;

/**
 * <p>
 * A CallbackClient is responsible for managing communication channels: channels
 * are created as needed (e.g., one per concurrent thread) and are closed after
 * a certain time.
 * </p>
 *
 * @author Barthelemy Dagenais
 *
 */
public class CallbackClient implements Py4JPythonClient {
	public final static String DEFAULT_ADDRESS = "127.0.0.1";

	protected final int port;

	protected final InetAddress address;

	protected final SocketFactory socketFactory;

	protected final Deque<Py4JClientConnection> connections = new ArrayDeque<Py4JClientConnection>();

	private final Lock lock = new ReentrantLock(true);

	private final Logger logger = Logger.getLogger(CallbackClient.class.getName());

	private boolean isShutdown = false;

	public final static long DEFAULT_MIN_CONNECTION_TIME = 30;

	private final ScheduledExecutorService executor = Executors.newScheduledThreadPool(1);

	protected final long minConnectionTime;

	protected final TimeUnit minConnectionTimeUnit;

	public CallbackClient(int port) {
		super();
		this.port = port;
		try {
			this.address = InetAddress.getByName(DEFAULT_ADDRESS);
		} catch (Exception e) {
			throw new Py4JNetworkException(
					"Default address could not be determined when creating communication channel.");
		}
		this.minConnectionTime = DEFAULT_MIN_CONNECTION_TIME;
		this.minConnectionTimeUnit = TimeUnit.SECONDS;
		this.socketFactory = SocketFactory.getDefault();
		setupCleaner();
	}

	public CallbackClient(int port, InetAddress address) {
		this(port, address, DEFAULT_MIN_CONNECTION_TIME, TimeUnit.SECONDS);
	}

	public CallbackClient(int port, InetAddress address, long minConnectionTime, TimeUnit minConnectionTimeUnit) {
		this(port, address, minConnectionTime, minConnectionTimeUnit, SocketFactory.getDefault());
	}

	/**
	 *
	 * @param port
	 *            The port used by channels to connect to the Python side.
	 * @param address
	 *            The addressed used by channels to connect to the Python side..
	 * @param minConnectionTime
	 *            The minimum connection time: channels are guaranteed to stay
	 *            connected for this time after sending a command.
	 * @param minConnectionTimeUnit
	 *            The minimum coonnection time unit.
	 * @param socketFactory
	 *            The non-{@code null} factory to make {@link Socket}s.
	 */
	public CallbackClient(int port, InetAddress address, long minConnectionTime, TimeUnit minConnectionTimeUnit,
			SocketFactory socketFactory) {
		super();
		this.port = port;
		this.address = address;
		this.minConnectionTime = minConnectionTime;
		this.minConnectionTimeUnit = minConnectionTimeUnit;
		this.socketFactory = socketFactory;
		setupCleaner();
	}

	public InetAddress getAddress() {
		return address;
	}

	protected Py4JClientConnection getConnection() throws IOException {
		Py4JClientConnection connection = null;

		connection = connections.pollLast();
		if (connection == null) {
			connection = new CallbackConnection(port, address, socketFactory);
			connection.start();
		}

		return connection;
	}

	protected Py4JClientConnection getConnectionLock() {
		Py4JClientConnection cc = null;
		try {
			logger.log(Level.INFO, "Getting CB Connection");
			lock.lock();
			if (!isShutdown) {
				cc = getConnection();
				logger.log(Level.INFO, "Acquired CB Connection");
			} else {
				logger.log(Level.INFO, "Shuting down, no connection can be created.");
			}
		} catch (Exception e) {
			logger.log(Level.SEVERE, "Critical error while sending a command", e);
			throw new Py4JException("Error while obtaining a new communication channel", e);
		} finally {
			lock.unlock();
		}

		return cc;
	}

	public int getPort() {
		return port;
	}

	/**
	 * <p>
	 * Creates a callback client which connects to the given address and port,
	 * but retains all the other settings (like the {@link #minConnectionTime}
	 * and the {@link #socketFactory}. This method is useful if for some reason
	 * your CallbackServer changes its address or you come to know of the
	 * address after Gateway has already instantiated.
	 * </p>
	 *
	 * @param pythonAddress
	 *            The address used by a PythonProxyHandler to connect to a
	 *            Python gateway.
	 * @param pythonPort
	 *            The port used by a PythonProxyHandler to connect to a Python
	 *            gateway. Essentially the port used for Python callbacks.
	 */
	@Override
	public Py4JPythonClient copyWith(InetAddress pythonAddress, int pythonPort) {
		return new CallbackClient(pythonPort, pythonAddress, minConnectionTime, minConnectionTimeUnit, socketFactory);
	}

	protected void giveBackConnection(Py4JClientConnection cc) {
		try {
			lock.lock();
			// TODO Does not make sense for PythonClient... the list will
			// just grow.
			if (cc != null) {
				if (!isShutdown) {
					connections.addLast(cc);
				} else {
					cc.shutdown();
				}
			}
		} finally {
			lock.unlock();
		}
	}

	/**
	 * <p>
	 * Closes communication channels that have not been used for a time
	 * specified at the creation of the callback client.
	 * </p>
	 *
	 * <p>
	 * Clients should not directly call this method: it is called by a periodic
	 * cleaner thread.
	 * </p>
	 *
	 */
	public void periodicCleanup() {
		try {
			lock.lock();
			if (!isShutdown) {
				int size = connections.size();
				for (int i = 0; i < size; i++) {
					Py4JClientConnection cc = connections.pollLast();
					if (cc.wasUsed()) {
						cc.setUsed(false);
						connections.addFirst(cc);
					} else {
						cc.shutdown();
					}
				}

			}
		} finally {
			lock.unlock();
		}
	}

	/**
	 * <p>
	 * Sends a command to the Python side. This method is typically used by
	 * Python proxies to call Python methods or to request the garbage
	 * collection of a proxy.
	 * </p>
	 *
	 * @param command
	 *            The command to send.
	 * @return The response.
	 */
	@Override
	public String sendCommand(String command) {
		return sendCommand(command, true);
	}

	/**
	 * <p>
	 * Sends a command to the Python side. This method is typically used by
	 * Python proxies to call Python methods or to request the garbage
	 * collection of a proxy.
	 * </p>
	 *
	 * @param command
	 *            The command to send.
	 * @param blocking
	 * 			  If the CallbackClient should wait for an answer (default
	 * 			  should be True, except for critical cases such as a
	 * 			  finalizer sending a command).
	 * @return The response.
	 */
	@Override
	public String sendCommand(String command, boolean blocking) {
		String returnCommand = null;
		Py4JClientConnection cc = getConnectionLock();

		if (cc == null) {
			throw new Py4JException("Cannot obtain a new communication channel");
		}

		try {
			returnCommand = cc.sendCommand(command, blocking);
			giveBackConnection(cc);
		} catch (Py4JNetworkException pe) {
			logger.log(Level.WARNING, "Error while sending a command", pe);
			cc.shutdown();
			if (shouldRetrySendCommand(cc, pe)) {
				// Retry in case the channel was dead.
				returnCommand = sendCommand(command, blocking);
			} else {
				throw new Py4JException("Error while sending a command.", pe);
			}
		} catch (Exception e) {
			logger.log(Level.SEVERE, "Critical error while sending a command", e);
			throw new Py4JException("Error while sending a command.");
		}

		return returnCommand;
	}

	protected boolean shouldRetrySendCommand(Py4JClientConnection cc, Py4JException pe) {
		return true;
	}

	protected void setupCleaner() {
		executor.scheduleAtFixedRate(new Runnable() {
			public void run() {
				periodicCleanup();
			}
		}, minConnectionTime, minConnectionTime, minConnectionTimeUnit);
	}

	/**
	 * <p>
	 * Closes all active channels, stops the periodic cleanup of channels and
	 * mark the client as shutting down.
	 *
	 * No more commands can be sent after this method has been called,
	 * <em>except</em> commands that were initiated before the shutdown method
	 * was called..
	 * </p>
	 */
	@Override
	public void shutdown() {
		logger.info("Shutting down Callback Client");
		try {
			lock.lock();
			isShutdown = true;
			for (Py4JClientConnection cc : connections) {
				cc.shutdown();
			}
			executor.shutdownNow();
			connections.clear();
		} finally {
			lock.unlock();
		}
	}
}
