package de.klierlinge.clear19.data.system;

import java.util.Arrays;

import de.klierlinge.clear19.App;
import de.klierlinge.clear19.data.DataProvider;
import oshi.SystemInfo;
import oshi.hardware.CentralProcessor.TickType;

public class CpuLoad extends DataProvider<CpuLoad.Data>
{
    private long[] lastTicks;
    
    public CpuLoad(App app, SystemInfo si)
    {
        super(new Data());
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
                updateData(new Data(currentLoad));
            }
            lastTicks = t;
        });
    }
    
    public static class Data
    {
        /**
         * CPU utilization that occurred while executing at the user level
         * (application).
         */
        public final double user;
        /**
         * CPU utilization that occurred while executing at the user level with nice
         * priority.
         */
        public final double nice;
        /**
         * CPU utilization that occurred while executing at the system level (kernel).
         */
        public final double system;
        /**
         * Time that the CPU or CPUs were idle and the system did not have an
         * outstanding disk I/O request.
         */
        public final double idle;
        /**
         * Time that the CPU or CPUs were idle during which the system had an
         * outstanding disk I/O request.
         */
        public final double iowait;
        /**
         * Time that the CPU used to service hardware IRQs
         */
        public final double irq;
        /**
         * Time that the CPU used to service soft IRQs
         */
        public final double softirq;
        /**
         * Time which the hypervisor dedicated for other guests in the system. Only
         * supported on Linux.
         */
        public final double steal;
        
        public Data(double[] d)
        {
            user = d[TickType.USER.getIndex()];
            nice = d[TickType.NICE.getIndex()];
            system = d[TickType.SYSTEM.getIndex()];
            idle = d[TickType.IDLE.getIndex()];
            iowait = d[TickType.IOWAIT.getIndex()];
            irq = d[TickType.IRQ.getIndex()];
            softirq = d[TickType.SOFTIRQ.getIndex()];
            steal = d[TickType.STEAL.getIndex()];
        }
        
        private Data()
        {
            user = nice = system = idle = iowait = irq = softirq = steal = 0;
        }
    }
}
