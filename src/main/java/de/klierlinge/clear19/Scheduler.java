package de.klierlinge.clear19;

import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.ScheduledThreadPoolExecutor;
import java.util.concurrent.ThreadFactory;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class Scheduler implements AutoCloseable
{
    private static final Logger logger = LogManager.getLogger(Scheduler.class.getName());

    private final ScheduledThreadPoolExecutor scheduler = new ScheduledThreadPoolExecutor(1,
            new DeamonThreadFactory(),
            (r, e) -> logger.error("Failed to execute task: " + r + " - " + e));

    public ScheduledFuture<?> schedule(long interval, Runnable task)
    {
        final var ctm = System.currentTimeMillis();
        final var delay = (ctm / interval + 1) * interval - ctm - 3;
        return scheduler.scheduleAtFixedRate(() -> {
            try
            {
                task.run();
            }
            catch(Throwable t)
            {
                logger.error("Error in scheduled task " + task, t);
                throw t;
            }
        }, delay, interval, TimeUnit.MILLISECONDS);
    }

    public ScheduledFuture<?> scheduleOnce(long delay, Runnable task)
    {
        return scheduler.schedule(task, delay, TimeUnit.MILLISECONDS);
    }

    @Override
    public void close()
    {
        scheduler.shutdownNow();
    }

    private static class DeamonThreadFactory implements ThreadFactory
    {
        private static final AtomicInteger poolNumber = new AtomicInteger(1);
        private final ThreadGroup group;
        private final AtomicInteger threadNumber = new AtomicInteger(1);
        private final String namePrefix;

        DeamonThreadFactory()
        {
            SecurityManager s = System.getSecurityManager();
            group = (s != null) ? s.getThreadGroup() : Thread.currentThread().getThreadGroup();
            namePrefix = "Scheduler Thread " + poolNumber.getAndIncrement();
        }

        @Override
        public Thread newThread(Runnable r)
        {
            Thread t = new Thread(group, r, namePrefix + ":" + threadNumber.getAndIncrement(), 0);
            if(!t.isDaemon())
                t.setDaemon(true);
            return t;
        }
    }
}
