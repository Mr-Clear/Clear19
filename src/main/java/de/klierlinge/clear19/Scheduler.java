package de.klierlinge.clear19;

import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.ScheduledThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class Scheduler implements AutoCloseable
{
    private static final Logger logger = LogManager.getLogger(Scheduler.class.getName());
    
    private final ScheduledThreadPoolExecutor scheduler = new ScheduledThreadPoolExecutor(1, (r, e) -> logger.error("Failed to execute task: " + r + " - " + e));
    
    public ScheduledFuture<?> schedule(long interval, Runnable task)
    {
        final var ctm = System.currentTimeMillis();
        final var delay = (ctm / interval + 1) * interval - ctm - 3;
        return scheduler.scheduleAtFixedRate(() -> {
            try
            {
                task.run();
            }
            catch (Throwable t)
            {
                logger.error("Error in scheduled task " + task, t);
                throw t;
            }
        }, delay, interval, TimeUnit.MILLISECONDS);
    }

    @Override
    public void close()
    {
        scheduler.shutdownNow();
    }
}
