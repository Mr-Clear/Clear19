package de.klierlinge.clear19.data.system;

import de.klierlinge.clear19.App;
import de.klierlinge.clear19.data.DataProvider;
import oshi.SystemInfo;

public class Memory extends DataProvider<Memory.Data>
{
    public Memory(App app, SystemInfo si)
    {
        super(new Data());
        app.schedule(1000, () -> {
            final var mem = si.getHardware().getMemory();
            final var vmem = mem.getVirtualMemory();
            updateData(new Data(mem.getTotal(), mem.getAvailable(), vmem.getSwapTotal(), vmem.getSwapUsed()));
        });
    }

    public static class Data
    {
        public final long total;
        public final long free;
        public final long swapTotal;
        public final long swapUsed;

        public Data(long total, long free, long swapTotal, long swapUsed)
        {
            super();
            /** The amount of actual physical memory, in bytes. */
            this.total = total;
            /** The amount of physical memory currently available, in bytes. */
            this.free = free;
            /**
             * The current size of the paging/swap file(s), in bytes. If the
             * paging/swap file can be extended, this is a soft limit.
             */
            this.swapTotal = swapTotal;
            /**
             * The current memory committed to the paging/swap file(s), in bytes
             */
            this.swapUsed = swapUsed;
        }

        private Data()
        {
            total = free = swapTotal = swapUsed = 0;
        }
    }

    public static String humanReadableByteCount(long bytes)
    {
        int unit = 1024;
        if(bytes < unit)
            return String.format("%d B  ", bytes);
        int exp = (int)(Math.log(bytes) / Math.log(unit));
        String pre = "KMGTPE".charAt(exp - 1) + "i";
        return String.format("%.1f %sB", bytes / Math.pow(unit, exp), pre);
    }
}
