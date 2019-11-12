package de.klierlinge.clear19.widgets;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

import de.klierlinge.clear19.widgets.geometry.Anchor;
import de.klierlinge.clear19.widgets.geometry.AnchoredPoint;
import de.klierlinge.clear19.widgets.geometry.Rectangle;
import de.klierlinge.clear19.widgets.geometry.Size;

class WidgetPlacement
{

    @Test
    void test()
    {
        final var root = new AppWidget<WidgetPlacement.Screens>()
        {
            @Override
            protected Screen getScreenByEnum(Screens screenEnum)
            {
                return null;
            }
        };
        root.setAbsRect(new Rectangle(new AnchoredPoint(0, 0, Anchor.TOP_LEFT), new Size(1000, 1000)));
        assertEquals(root.getAbsRect(), new Rectangle(new AnchoredPoint(0, 0, Anchor.TOP_LEFT), new Size(1000, 1000)));
        ContainerWidget level1 = new ContainerWidget(root);
    }

    static enum Screens {}
}
