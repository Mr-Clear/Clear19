package de.klierlinge.clear19.data.system;

import java.util.Arrays;

import de.klierlinge.clear19.App;
import de.klierlinge.clear19.data.DataProvider;
import oshi.SystemInfo;
import oshi.hardware.CentralProcessor.TickType;

public class CpuUsage extends DataProvider<CpuUsage.UsageData>
{
    private long[] lastTicks;
    
    public CpuUsage(App app, SystemInfo si)
    {
        app.schedule(1000, () -> {
            final var t = si.getHardware().getProcessor().getSystemCpuLoadTicks();
            if (lastTicks != null)
            {
                final long[] diff = new long[t.length];
                for(int i = 0; i < t.length; i++)
                {
                    diff[i] = (t[i] - lastTicks[i]);
                }
                final var sum = Arrays.stream(diff).sum();
                final var currentLoad = Arrays.stream(diff).mapToDouble(d -> (double)d / sum).toArray();
                updateData(new UsageData(currentLoad));
            }
            lastTicks = t;
        });
    }
    
    public static class UsageData
    {
        /**
         * CPU utilization that occurred while executing at the user level
         * (application).
         */
        final double user;
        /**
         * CPU utilization that occurred while executing at the user level with nice
         * priority.
         */
        final double nice;
        /**
         * CPU utilization that occurred while executing at the system level (kernel).
         */
        final double system;
        /**
         * Time that the CPU or CPUs were idle and the system did not have an
         * outstanding disk I/O request.
         */
        final double idle;
        /**
         * Time that the CPU or CPUs were idle during which the system had an
         * outstanding disk I/O request.
         */
        final double iowait;
        /**
         * Time that the CPU used to service hardware IRQs
         */
        final double irq;
        /**
         * Time that the CPU used to service soft IRQs
         */
        final double softirq;
        /**
         * Time which the hypervisor dedicated for other guests in the system. Only
         * supported on Linux.
         */
        final double steal;
        public UsageData(double[] d)
        {
            this.user = d[TickType.USER.getIndex()];
            this.nice = d[TickType.NICE.getIndex()];
            this.system = d[TickType.SYSTEM.getIndex()];
            this.idle = d[TickType.IDLE.getIndex()];
            this.iowait = d[TickType.IOWAIT.getIndex()];
            this.irq = d[TickType.IRQ.getIndex()];
            this.softirq = d[TickType.SOFTIRQ.getIndex()];
            this.steal = d[TickType.STEAL.getIndex()];
        }
    }
}
