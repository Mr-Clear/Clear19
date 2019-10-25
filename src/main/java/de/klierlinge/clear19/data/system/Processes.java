package de.klierlinge.clear19.data.system;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.stream.Collectors;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.hyperic.sigar.Sigar;
import org.hyperic.sigar.SigarException;

import de.klierlinge.clear19.App;
import de.klierlinge.clear19.data.DataProvider;

public class Processes extends DataProvider<Map<Long, Processes.ProcessData>>
{
    private static final Logger logger = LogManager.getLogger(Processes.class.getName());

    private static final long UPDATE_INTERVAL = 1000;
    private final Sigar si;
    private final int cpuCount;

    public Processes(App app, Sigar si)
    {
        super(new HashMap<>(0));
        this.si = si;
        int tcpuCount;
        try
        {
            tcpuCount = si.getCpuList().length;
        }
        catch(SigarException e)
        {
            tcpuCount = 1;
            logger.error("Failed to get cpu count.", e);
        }
        cpuCount = tcpuCount;
        app.schedule(UPDATE_INTERVAL, () -> update());
    }

    private void update()
    {
        var s = System.currentTimeMillis();
        try
        {
            final var map = Arrays.stream(si.getProcList())
                                  .boxed()
                                  .collect(Collectors.toMap(pid -> pid, pid -> new ProcessData(si, pid)));

            System.out.println(System.currentTimeMillis() - s);
            updateData(map);
        }
        catch(SigarException e)
        {
            logger.error("Failed to get process list.", e);
        }
    }

    public class ProcessData
    {
        public final long pid;
        public final long ppid;
        public final String name;
        public final long userTime;
        public final long kernelTime;
        public final double userLoad;
        public final double kernelLoad;
        public final long memory;

        public ProcessData(Sigar si, long pid)
        {
            this.pid = pid;

            long tppid;
            String tname;
            try
            {
                final var stat = si.getProcState(pid);
                tppid = stat.getPpid();
                tname = stat.getName();
            }
            catch(SigarException e)
            {
                tppid = -1;
                tname = null;
                logger.error("Failed to get process state.", e);
            }
            ppid = tppid;
            name = tname;

            long tuserTime;
            long tkernelTime;
            try
            {
                final var time = si.getProcTime(pid);
                tuserTime = time.getUser();
                tkernelTime = time.getSys();
            }
            catch(SigarException e)
            {
                tuserTime = -1;
                tkernelTime = -1;
                logger.trace("Failed to get process time.", e);
            }
            userTime = tuserTime;
            kernelTime = tkernelTime;

            long tmemory;
            try
            {
                tmemory = si.getProcMem(pid).getSize();
            }
            catch(SigarException e)
            {
                tmemory = -1;
                logger.trace("Failed to get process memory.", e);
            }
            memory = tmemory;

            final var lastP = getData().get(pid);
            if(lastP != null)
            {
                userLoad = (userTime - lastP.userTime) / 1000.0 / cpuCount;
                kernelLoad = (kernelTime - lastP.kernelTime) / 1000.0 / cpuCount;
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
