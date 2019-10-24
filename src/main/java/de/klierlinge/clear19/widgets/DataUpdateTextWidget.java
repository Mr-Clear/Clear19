package de.klierlinge.clear19.widgets;

import java.util.function.Function;

import de.klierlinge.clear19.data.DataProvider;

public class DataUpdateTextWidget extends TextWidget
{
    public <T> DataUpdateTextWidget(Widget parent, DataProvider<T> provider, Function<T, String> onUpdate)
    {
        super(parent, onUpdate.apply(provider.getData()));
        provider.addListener((d) -> setText(onUpdate.apply(d)));
    }
}
