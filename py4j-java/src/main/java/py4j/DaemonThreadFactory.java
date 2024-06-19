package py4j;

import java.util.concurrent.ThreadFactory;
import java.util.concurrent.atomic.AtomicInteger;

public class DaemonThreadFactory implements ThreadFactory {
    private final String threadNamePrefix;
    private final AtomicInteger counter = new AtomicInteger();

    public DaemonThreadFactory(String threadNamePrefix) {
        this.threadNamePrefix = threadNamePrefix;
    }

    public Thread newThread(Runnable r) {
        Thread t = new Thread(r);
        t.setDaemon(true);
        t.setName(this.threadNamePrefix + "-" + this.counter.getAndIncrement());
        return t;
    }
}