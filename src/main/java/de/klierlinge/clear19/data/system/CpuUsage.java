package de.klierlinge.clear19.data.system;

import java.util.Arrays;

import de.klierlinge.clear19.App;
import oshi.SystemInfo;
import oshi.hardware.CentralProcessor.TickType;

public class CpuUsage
{
    private final SystemInfo si = new SystemInfo();
    private static final int TYPE_COUNT = TickType.values().length;
    private long[] lastTicks;
    public double[] currentLoad = new double[TYPE_COUNT]; 
    
    public CpuUsage(App app)
    {
        app.schedule(1000, () -> {
            final var t = si.getHardware().getProcessor().getSystemCpuLoadTicks();
            if (lastTicks != null)
            {
                final long[] diff = new long[TYPE_COUNT];
                for(int i = 0; i < t.length; i++)
                {
                    diff[i] = (t[i] - lastTicks[i]);
                }
                final var sum = Arrays.stream(diff).sum();
                currentLoad = Arrays.stream(diff).mapToDouble(d -> (double)d / sum).toArray();
            }
            lastTicks = t;
        });
    }
    
    public double getIdleLoad()
    {
        return currentLoad[TickType.IDLE.getIndex()];
    }
    
    public double getUserLoad()
    {
        return currentLoad[TickType.USER.getIndex()];
    }
    
    public double getSystemLoad()
    {
        return currentLoad[TickType.SYSTEM.getIndex()];
    }
    
    public double getIrqLoad()
    {
        return currentLoad[TickType.IRQ.getIndex()];
    }
    
    public double getSoftIrqLoad()
    {
        return currentLoad[TickType.SOFTIRQ.getIndex()];
    }
}
