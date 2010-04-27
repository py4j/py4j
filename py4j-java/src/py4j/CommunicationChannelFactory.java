package py4j;

import java.io.IOException;
import java.net.InetAddress;
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * <p>
 * A CommunicationChannelFactory is responsible for managing communication
 * channels: channels are created as needed (e.g., one per concurrent thread)
 * and are closed after a certain time.
 * </p>
 * 
 * @author Barthelemy Dagenais
 * 
 */
public class CommunicationChannelFactory {
	private final int port;

	private final InetAddress address;

	private final Deque<CommunicationChannel> channels = new ArrayDeque<CommunicationChannel>();

	private final Lock lock = new ReentrantLock(true);

	private final Logger logger = Logger
			.getLogger(CommunicationChannelFactory.class.getName());

	private boolean isShutdown = false;

	public final static long DEFAULT_MIN_CONNECTION_TIME = 30;

	private final ScheduledExecutorService executor = Executors
			.newScheduledThreadPool(1);

	private final long minConnectionTime;

	private final TimeUnit minConnectionTimeUnit;

	public CommunicationChannelFactory(int port) {
		super();
		this.port = port;
		try {
			this.address = InetAddress.getByName("localhost");
		} catch (Exception e) {
			throw new Py4JNetworkException(
					"Local Host could not be determined when creating communication channel.");
		}
		this.minConnectionTime = DEFAULT_MIN_CONNECTION_TIME;
		this.minConnectionTimeUnit = TimeUnit.SECONDS;
		setupCleaner();
	}

	public CommunicationChannelFactory(int port, InetAddress address) {
		super();
		this.port = port;
		this.address = address;
		this.minConnectionTime = DEFAULT_MIN_CONNECTION_TIME;
		this.minConnectionTimeUnit = TimeUnit.SECONDS;
		setupCleaner();
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
	 */
	public CommunicationChannelFactory(int port, InetAddress address,
			long minConnectionTime, TimeUnit minConnectionTimeUnit) {
		super();
		this.port = port;
		this.address = address;
		this.minConnectionTime = minConnectionTime;
		this.minConnectionTimeUnit = minConnectionTimeUnit;
		setupCleaner();
	}

	private void setupCleaner() {
		executor.scheduleAtFixedRate(new Runnable() {
			public void run() {
				periodicCleanup();
			}
		}, minConnectionTime, minConnectionTime, minConnectionTimeUnit);
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
	public String sendCommand(String command) {
		String returnCommand = null;
		CommunicationChannel cc = getChannelLock();

		if (cc == null) {
			throw new Py4JException("Cannot obtain a new communication channel");
		}

		try {
			returnCommand = cc.sendCommand(command);
		} catch (Py4JNetworkException pe) {
			logger.log(Level.WARNING, "Error while sending a command", pe);
			// Retry in case the channel was dead.
			returnCommand = sendCommand(command);
		} catch (Exception e) {
			logger.log(Level.SEVERE, "Critical error while sending a command",
					e);
			throw new Py4JException("Error while sending a command.");
		}

		giveBackChannel(cc);

		return returnCommand;
	}

	/**
	 * <p>
	 * Closes all active channels, stops the periodic cleanup of channels and
	 * mark the factory as shutting down.
	 * 
	 * No more commands can be send after this method has been called,
	 * <em>except</em> commands that were initiated before the shutdown method
	 * was called..
	 * </p>
	 */
	public void shutdown() {
		logger.info("Shutting down Communication Channel Factory");
		try {
			lock.lock();
			isShutdown = true;
			for (CommunicationChannel cc : channels) {
				cc.shutdown();
			}
			executor.shutdownNow();
			channels.clear();
		} finally {
			lock.unlock();
		}
	}

	/**
	 * <p>
	 * Closes communication channels that have not been used for a time
	 * specified at the creation of the communication channel factory.
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
				int size = channels.size();
				for (int i = 0; i < size; i++) {
					CommunicationChannel cc = channels.getLast();
					if (cc.wasUsed()) {
						cc.setUsed(false);
						channels.addFirst(cc);
					} else {
						cc.shutdown();
					}
				}

			}
		} finally {
			lock.unlock();
		}
	}

	private CommunicationChannel getChannelLock() {
		CommunicationChannel cc = null;
		try {
			lock.lock();
			if (!isShutdown) {
				cc = getChannel();
			}
		} catch (Exception e) {
			logger.log(Level.SEVERE, "Critical error while sending a command",
					e);
			throw new Py4JException(
					"Error while obtaining a new communication channel", e);
		} finally {
			lock.unlock();
		}

		return cc;
	}

	private void giveBackChannel(CommunicationChannel cc) {
		try {
			lock.lock();
			if (cc != null) {
				if (!isShutdown) {
					channels.addLast(cc);
				} else {
					cc.shutdown();
				}
			}
		} finally {
			lock.unlock();
		}
	}

	private CommunicationChannel getChannel() throws IOException {
		CommunicationChannel channel = null;

		channel = channels.pollLast();
		if (channel == null) {
			channel = new DefaultCommunicationChannel(port, address);
			channel.start();
		}

		return channel;
	}
}
