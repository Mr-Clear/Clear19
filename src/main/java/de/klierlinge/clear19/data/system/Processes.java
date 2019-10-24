package de.klierlinge.clear19.data.system;

import java.util.HashMap;
import java.util.Map;

import de.klierlinge.clear19.App;
import de.klierlinge.clear19.data.DataProvider;
import oshi.SystemInfo;
import oshi.software.os.OSProcess;
import oshi.software.os.OperatingSystem.ProcessSort;

public class Processes extends DataProvider<Map<Integer, Processes.ProcessData>>
{
    private static final long UPDATE_INTERVAL = 1000;
    private final SystemInfo si;
    
    public Processes(App app, SystemInfo si)
    {
        super(new HashMap<>(0));
        this.si = si;
        app.schedule(UPDATE_INTERVAL, () -> update());
    }
    
    private void update()
    {
        var s = System.currentTimeMillis();
        final var ps = si.getOperatingSystem().getProcesses(0, ProcessSort.PID);
        System.out.println(System.currentTimeMillis() - s);
        final var map = new HashMap<Integer, Processes.ProcessData>();
        for (final var p : ps)
        {
            map.put(p.getProcessID(), new ProcessData(p));
        }
        updateData(map);
    }

    public class ProcessData
    {
        public final int PID;
        public final int PPID;
        public final String name;
        public final String user;
        public final long userTime;
        public final long kernelTime;
        public final double userLoad;
        public final double kernelLoad;
        public final byte bitness;
        public final long memory;
        
        public ProcessData(OSProcess p)
        {
            PID = p.getProcessID();
            PPID = p.getParentProcessID();
            name = p.getName();
            user = p.getUser();
            userTime = p.getUserTime();
            kernelTime = p.getKernelTime();
            memory = p.getVirtualSize();
            bitness = (byte)p.getBitness();
            
            final var lastP = getData().get(PID);
            if (lastP != null)
            {
                userLoad = (userTime - lastP.userTime) / 1000.0;
                kernelLoad = (kernelTime - lastP.kernelTime) / 1000.0;
            }
            else
            {
                userLoad = kernelLoad = 0;
            }
        }
        
        public double totalTime()
        {
            return userTime + kernelTime;
        }
        
        public double totalLoad()
        {
            return userLoad + kernelLoad;
        }
    }
}
