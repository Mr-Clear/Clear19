package de.klierlinge.clear19.widgets;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import de.klierlinge.clear19.Scheduler;
import de.klierlinge.clear19.data.system.SystemData;

public abstract class AppWidget<T extends Enum<T>> extends ContainerWidget
{
    private static final Logger logger = LogManager.getLogger(AppWidget.class.getName());
    
    private final Scheduler scheduler = new Scheduler();
    private final SystemData systemData = new SystemData();
    private T currentScreenEnum;
    
    public AppWidget()
    {
        super(null);
    }

    public Scheduler getScheduler()
    {
        return scheduler;
    }

    public SystemData getSystemData()
    {
        return systemData;
    }
    
    public Screen getCurrentScreen()
    {
        return (Screen)getChildren().get(0);
    }

    public T setCurrentScreen(T screenEnum)
    {
        final var lastScreenEnum = getCurrentScreenEnum();
        final var lastScreen = getCurrentScreen();
        final var nextScreen = getScreenByEnum(screenEnum);
        if(screenEnum != getCurrentScreenEnum())
        {
            lastScreen.onHide(nextScreen);
            getChildren().clear();
            getChildren().add(nextScreen);
            nextScreen.onShow(lastScreen);
            nextScreen.setDirty(true);
            currentScreenEnum = screenEnum;
            logger.debug("Changed Screen from " + lastScreen.getName() + " to " + nextScreen.getName() + ".");
        }
        return lastScreenEnum;
    }

    public T getCurrentScreenEnum()
    {
        return currentScreenEnum;
    }
    
    abstract protected Screen getScreenByEnum(T screenEnum);
}
