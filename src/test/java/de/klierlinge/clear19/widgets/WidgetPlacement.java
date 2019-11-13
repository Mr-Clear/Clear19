package de.klierlinge.clear19.widgets;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.awt.Graphics2D;

import org.junit.jupiter.api.Test;

import de.klierlinge.clear19.widgets.Border.Orientation;
import de.klierlinge.clear19.widgets.geometry.Anchor;
import de.klierlinge.clear19.widgets.geometry.AnchorH;
import de.klierlinge.clear19.widgets.geometry.AnchoredPoint;
import de.klierlinge.clear19.widgets.geometry.Rectangle;
import de.klierlinge.clear19.widgets.geometry.Size;

class WidgetPlacement
{
    @SuppressWarnings("static-method")
    @Test
    void deepNesting()
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
        assertEquals(new Rectangle(new AnchoredPoint(0, 0, Anchor.TOP_LEFT), new Size(1000, 1000)), root.getAbsRect());
        assertEquals(new Rectangle(new AnchoredPoint(0, 0, Anchor.TOP_LEFT), new Size(1000, 1000)), root.getRectangle());
        
        final var level1 = new ContainerWidget(root);
        level1.setRectangle(new AnchoredPoint(10, 20, Anchor.TOP_LEFT), new Size(500, 500));
        assertEquals(new AnchoredPoint(10, 20, Anchor.TOP_LEFT),level1.getPosition(Anchor.TOP_LEFT));
        assertEquals(new AnchoredPoint(510, 520, Anchor.BOTTOM_RIGHT),level1.getPosition(Anchor.BOTTOM_RIGHT));
        assertEquals(new AnchoredPoint(260, 270, Anchor.CENTER_CENTER),level1.getPosition(Anchor.CENTER_CENTER));

        final var level2 = new ContainerWidget(level1);
        level2.setRectangle(new AnchoredPoint(30, 10, Anchor.TOP_LEFT), new Size(200, 200));
        assertEquals(new AnchoredPoint(30, 10, Anchor.TOP_LEFT),level2.getPosition(Anchor.TOP_LEFT));
        assertEquals(new AnchoredPoint(230, 210, Anchor.BOTTOM_RIGHT),level2.getPosition(Anchor.BOTTOM_RIGHT));
        assertEquals(new AnchoredPoint(130, 110, Anchor.CENTER_CENTER),level2.getPosition(Anchor.CENTER_CENTER));

        final var level3 = new ContainerWidget(level2);
        level3.setRectangle(new AnchoredPoint(10, 10, Anchor.TOP_LEFT), new Size(100, 100));
        assertEquals(new AnchoredPoint(10, 10, Anchor.TOP_LEFT),level3.getPosition(Anchor.TOP_LEFT));
        assertEquals(new AnchoredPoint(110, 110, Anchor.BOTTOM_RIGHT),level3.getPosition(Anchor.BOTTOM_RIGHT));
        assertEquals(new AnchoredPoint(60, 60, Anchor.CENTER_CENTER),level3.getPosition(Anchor.CENTER_CENTER));
        assertEquals(new Rectangle(50, 40, 100, 100, Anchor.TOP_LEFT),level3.getAbsRect());
        
        final var b1 = new Border(level3, Orientation.HORIZONTAL);
        b1.setRectangle(level3.getSize().getPos(Anchor.CENTER_CENTER), new Size(level3.getWidth(), b1.getPreferedSize(null).getHeight()));
        assertEquals(new AnchoredPoint(0, 49, Anchor.TOP_LEFT), b1.getPosition(Anchor.TOP_LEFT));
        assertEquals(new AnchoredPoint(100, 52, Anchor.BOTTOM_RIGHT), b1.getPosition(Anchor.BOTTOM_RIGHT));

        final var b2 = new Border(level3, Orientation.VERTICAL);
        b2.setRectangle(b1.getPosition(Anchor.BOTTOM_CENTER).anchored(Anchor.TOP_CENTER), level3.getSize().getPos(Anchor.BOTTOM_CENTER));
        assertEquals(new AnchoredPoint(50, 52, Anchor.TOP_LEFT), b2.getPosition(Anchor.TOP_LEFT));
        assertEquals(new AnchoredPoint(50, 100, Anchor.BOTTOM_RIGHT), b2.getPosition(Anchor.BOTTOM_RIGHT));
        b2.setWidth(b2.getPreferedSize(null).getWidth(), AnchorH.CENTER);
        assertEquals(new AnchoredPoint(49, 52, Anchor.TOP_LEFT), b2.getPosition(Anchor.TOP_LEFT));
        assertEquals(new AnchoredPoint(52, 100, Anchor.BOTTOM_RIGHT), b2.getPosition(Anchor.BOTTOM_RIGHT));
        assertEquals(100, b1.getWidth());
        assertEquals(  3, b1.getHeight());
        assertEquals(  0, b1.getLeft());
        assertEquals(100, b1.getRight());
        assertEquals( 49, b1.getTop());
        assertEquals( 52, b1.getBottom());
        assertEquals(  3, b2.getWidth());
        assertEquals( 48, b2.getHeight());
        assertEquals( 52, b2.getTop());
        assertEquals( 49, b2.getLeft());
        assertEquals( 52, b2.getRight());
        assertEquals(100, b2.getBottom());
        
        final var w1 = new DummyWidget(level3);
        w1.setRectangle(b2.getPosition(Anchor.TOP_RIGHT).anchored(Anchor.TOP_LEFT), level3.getSize().toVector());
        assertEquals(new Rectangle(102, 92, 48, 48, Anchor.TOP_LEFT), w1.getAbsRect());
    }

    private enum Screens { /* Not needed. */ }
    private static class DummyWidget extends Widget
    {
        public DummyWidget(ContainerWidget parent)
        {
            super(parent);
        }
        @Override
        public void paintForeground(Graphics2D g)
        { /* Don't paint anything. */ }
    }
}
