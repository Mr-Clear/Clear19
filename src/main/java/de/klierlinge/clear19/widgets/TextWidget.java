package de.klierlinge.clear19.widgets;

import java.awt.Font;
import java.awt.FontMetrics;
import java.awt.Graphics2D;
import java.util.Objects;

import de.klierlinge.clear19.widgets.geometry.Size;

public class TextWidget extends Widget
{
    private String text;
    private HAllignment hAllignment = HAllignment.LEFT;
    private VAllignment vAllignment = VAllignment.TOP;
    private Font font = new Font(Font.DIALOG, 0, 8);

    public TextWidget(ContainerWidget parent, String text)
    {
        super(parent);
        setText(text);
    }

    @Override
    public void paintForeground(Graphics2D g)
    {
        g.setColor(getForeground());
        g.setFont(font);
        final FontMetrics fontMetrics = g.getFontMetrics();
        final var fontHeight = fontMetrics.getHeight();
        final var fontAscent = fontMetrics.getAscent();
        final var fontDescent = fontMetrics.getDescent();
        final var split = text.split("\n");
        
        final var textHeight = split.length * fontHeight - fontDescent;
        final var top = switch(vAllignment)
                {
                    case TOP -> 0;
                    case CENTER ->(getHeight() - textHeight) / 2;
                    case BOTTOM -> getHeight() - textHeight;
                };
        
        int line = 0;
        for (String string : split)
        {
            final var stringWidth = fontMetrics.stringWidth(string);
            final var x = switch(hAllignment)
                    {
                        case LEFT -> 0;
                        case CENTER -> (getWidth() - stringWidth) / 2;
                        case RIGHT -> getWidth() - stringWidth;
                    };
            final var y = top + fontHeight * line + fontAscent;
            g.drawString(string, x, y);
            line++;
        }
    }
    
    @Override
    public Size getPreferedSize(Graphics2D g)
    {
        return getPreferedSize(g, font, text);
    }
    
    public static Size getPreferedSize(Graphics2D g, Font testFont, String testText)
    {
        if(g == null)
        {
            return new Size(100, 10);
        }
        g.setFont(testFont);
        final FontMetrics fontMetrics = g.getFontMetrics();
        final var fontHeight = fontMetrics.getHeight();
        final var fontDescent = fontMetrics.getDescent();
        final var split = testText.split("\n");
        var max = 0;
        for (String string : split)
        {
            final var stringWidth = fontMetrics.stringWidth(string);
            if (stringWidth > max)
                max = stringWidth;
        }
        return new Size(max, split.length * fontHeight - fontDescent);
    }
    
    public void fitFontSize(Graphics2D g)
    {
        fitFontSize(g, getSize());
    }
    
    public void fitFontSize(Graphics2D g, Size size)
    {
        final var testSize = getPreferedSize(g);
        final var sx = (float)testSize.getWidth() / size.getWidth();
        final var sy = (float)testSize.getHeight() / size.getHeight();
        final var fontSize = getFont().getSize2D() / Math.max(sx, sy);
        setFont(getFont().deriveFont(fontSize));
    }

    public String getText()
    {
        return text;
    }

    public void setText(String text)
    {
        if(!Objects.equals(this.text, text))
        {
            this.text = text;
            setDirty();
        }
    }

    public HAllignment getHAllignment()
    {
        return hAllignment;
    }

    public void setHAllignment(HAllignment hAllignment)
    {
        if (this.hAllignment != hAllignment)
        {
            this.hAllignment = hAllignment;
            setDirty();
        }
    }

    public VAllignment getvAllignment()
    {
        return vAllignment;
    }

    public void setvAllignment(VAllignment vAllignment)
    {
        this.vAllignment = vAllignment;
    }

    public Font getFont()
    {
        return font;
    }

    public void setFont(Font font)
    {
        if(!Objects.equals(this.font, font))
        {
            this.font = font;
            setDirty();
        }
    }

    public enum HAllignment
    {
        LEFT,
        CENTER,
        RIGHT
    }

    public enum VAllignment
    {
        TOP,
        CENTER,
        BOTTOM
    }
}
