package de.klierlinge.clear19.widgets;

import java.util.function.Supplier;

public class AutoUpdateTextWidget extends TextWidget
{
    public AutoUpdateTextWidget(Widget parent, long updateInterval, Supplier<String> supplier)
    {
        super(parent, supplier.get());
        app.schedule(updateInterval, () -> setText(supplier.get()));
    }
}
