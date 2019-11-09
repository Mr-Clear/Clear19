package de.klierlinge.clear19.data;

import java.util.HashSet;
import java.util.Set;
import java.util.function.Consumer;

public class DataProvider<T>
{
    private final Set<Consumer<T>> listeners = new HashSet<>();
    private T data;
    
    protected DataProvider(T initialData)
    {
        data= initialData;
    }
    
    protected void updateData(T newData)
    {
        data = newData;
        synchronized(listeners)
        {
            for(final var l : listeners)
                l.accept(data);
        }
    }
    
    public T getData()
    {
        return data;
    }
    
    public boolean addListener(Consumer<T> listener)
    {
        synchronized(listeners)
        {
            return listeners.add(listener);
        }
    }
    
    public boolean removeListener(Consumer<T> listener)
    {
        synchronized(listeners)
        {
            return listeners.remove(listener);
        }
    }
}
