package de.klierlinge.clear19.data.system;

import org.hyperic.sigar.Sigar;

import de.klierlinge.clear19.Scheduler;

public class SystemData
{
    public final Scheduler scheduler = new Scheduler();

    public final Sigar si;
    public final CpuLoad cpuLoad;
    public final Memory memory;
    public final Processes processes;
    
    public SystemData()
    {
        si = new Sigar();
        cpuLoad = new CpuLoad(si, scheduler);
        memory = new Memory(si, scheduler);
        processes = new Processes(si, scheduler);
    }
}
