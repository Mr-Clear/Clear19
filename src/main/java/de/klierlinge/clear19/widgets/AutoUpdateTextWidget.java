package de.klierlinge.clear19.widgets;

import java.util.function.Supplier;

public class AutoUpdateTextWidget extends TextWidget
{
    public AutoUpdateTextWidget(ContainerWidget parent, long updateInterval, Supplier<String> supplier)
    {
        super(parent, supplier.get());
        getApp().scheduler.schedule(updateInterval, () -> setText(supplier.get()));
    }
}
