package de.klierlinge.clear19.data.system;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.hyperic.sigar.Mem;
import org.hyperic.sigar.Sigar;
import org.hyperic.sigar.SigarException;

import de.klierlinge.clear19.App;
import de.klierlinge.clear19.data.DataProvider;

public class Memory extends DataProvider<Memory.Data>
{
    private static final Logger logger = LogManager.getLogger(Memory.class.getName());
    
    public Memory(App app, Sigar si)
    {
        super(new Data());
        app.schedule(1000, () -> {
            try
            {
                updateData(new Data(si.getMem()));
            }
            catch(SigarException e)
            {
                logger.error("Failed to load memory statistics.", e);
            }
        });
    }

    public static class Data
    {
        public final long total;
        public final long free;

        private Data()
        {
            total = free = 0;
        }

        public Data(Mem mem)
        {
            total = mem.getTotal();
            free = mem.getFree();
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
