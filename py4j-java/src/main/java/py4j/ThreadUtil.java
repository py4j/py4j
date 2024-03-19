package py4j;

import java.util.concurrent.ThreadFactory;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * <p>
 * Thread utility class providing a method to create threads.
 * </p>
 *
 * @author Alex Archambault
 *
 */
public class ThreadUtil {

    private static ThreadFactory factory = new ThreadFactory() {
        private final AtomicInteger counter = new AtomicInteger();
        @Override
        public Thread newThread(Runnable r) {
            int index = counter.incrementAndGet();
            String name = "py4j-" + index;
            Thread thread = new Thread(r, name);
            thread.setDaemon(true);
            return thread;
        }
    };

    public static Thread createThread(Runnable runnable) {
        return factory.newThread(runnable);
    }
}
