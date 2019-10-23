package de.klierlinge.clear19.data.system;

import java.util.Arrays;

import de.klierlinge.clear19.App;
import oshi.SystemInfo;

public class CpuUsage
{
    private final SystemInfo si = new SystemInfo();
    //private final Queue<long[]> ticks = new LinkedList<>();
    private long[] lastTicks;
    public final float[] currentLoad = new float[8]; 
    
    public CpuUsage(App app)
    {
        app.schedule(100, () -> {
            final var t = si.getHardware().getProcessor().getSystemCpuLoadTicks();
            final var sum = (float)Arrays.stream(t).sum();
            System.out.println(sum);
            for(int i = 0; i < t.length; i++)
            {
                currentLoad[i] = (t[i] - lastTicks[i]) / sum;
            }
            lastTicks = t;
        });
    }
}
