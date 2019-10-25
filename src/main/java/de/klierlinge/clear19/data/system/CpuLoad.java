package de.klierlinge.clear19.data.system;

import java.lang.reflect.Field;
import java.util.Arrays;
import java.util.Iterator;
import java.util.Map;
import java.util.function.BiFunction;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.hyperic.sigar.Cpu;
import org.hyperic.sigar.Sigar;
import org.hyperic.sigar.SigarException;

import de.klierlinge.clear19.App;
import de.klierlinge.clear19.data.DataProvider;

public class CpuLoad extends DataProvider<CpuLoad.Data>
{
    private static final Logger logger = LogManager.getLogger(CpuLoad.class.getName());
    
    Cpu lastCpu;
    
    public CpuLoad(App app, Sigar si)
    {
        super(new Data());
        app.schedule(1000, () -> {
                try
                {
                    final var cpu = si.getCpu();
                    if (lastCpu != null)
                    {
                        final var diffs = merge(cpuStream(cpu), cpuStream(lastCpu),
                                (a, b) -> new CpuField(a.name,  a.value - b.value))
                                .collect(Collectors.toList());
                        final var total = diffs.stream()
                                               .filter((f) -> f.name == "total")
                                               .findFirst()
                                               .get()
                                               .value;
                        final var load = diffs.stream()
                                              .collect(Collectors.toMap((f) -> f.name, (f) -> (double)f.value / total));
                        updateData(new Data(load));
                    }
                    lastCpu = cpu;
                }
                catch(SigarException e)
                {
                    logger.error("Failed to load CPU statistics.", e);
                }
        });
    }
        
    private static class CpuField
    {
        private final String name;
        private final long value;
        private CpuField(String name, long value)
        {
            this.name = name;
            this.value = value;
        }
        private CpuField(Field field, Cpu object)
        {
            this.name = field.getName();
            long v;
            try
            {
                v = field.getLong(object);
            }
            catch(IllegalArgumentException | IllegalAccessException e)
            {
                logger.error("Failed to read CPU statistics.", e);
                v = -1;
            }
            value = v;
        }
    }
    
    private static Stream<CpuField> cpuStream(Cpu cpu)
    {
        final Field[] fields = Cpu.class.getDeclaredFields();
        Arrays.stream(fields).forEach((f) -> f.setAccessible(true));
        return Arrays.stream(fields).filter((f) -> f.getType() == long.class).map((f) -> new CpuField(f, cpu));
    }
    
    static <A, B, R> Stream<R> merge(Stream<A> as, Stream<B> bs, BiFunction<A, B, R> function)
    {
        Iterator<A> i = as.iterator();
        return bs.filter(x -> i.hasNext())
                  .map(b -> function.apply(i.next(), b));
    }
    
    public static class Data
    {
        public final double user;
        public final double nice;
        public final double sys;
        public final double idle;
        public final double wait;
        public final double irq;
        public final double softIrq;
        public final double stolen;
        public final double total;
        
        public Data(Map<String, Double> map)
        {
            user = map.get("user");
            nice = map.get("nice");
            sys = map.get("sys");
            idle = map.get("idle");
            wait = map.get("wait");
            irq = map.get("irq");
            softIrq = map.get("softIrq");
            stolen = map.get("stolen");
            total = map.get("total");
        }
        
        private Data()
        {
            user = nice = sys = idle = wait = irq = softIrq = stolen = total = 0;
        }
    }
}
