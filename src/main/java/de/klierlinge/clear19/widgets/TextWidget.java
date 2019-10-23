package de.klierlinge.clear19.widgets;

import java.awt.Dimension;
import java.awt.Font;
import java.awt.FontMetrics;
import java.awt.Graphics2D;
import java.util.Objects;

public class TextWidget extends Widget
{
    private String text;
    private HAllignment hAllignment = HAllignment.LEFT;
    private VAllignment vAllignment = VAllignment.TOP;
    private Font font;

    public TextWidget(Widget parent, String text)
    {
        super(parent);
        setText(text);
    }

    @Override
    public void paintForeground(Graphics2D g)
    {
        g.setFont(font);
        g.setColor(getForeground());
        final FontMetrics fontMetrics = g.getFontMetrics();
        final int fontHeight = fontMetrics.getHeight();
        final int fontAscent = fontMetrics.getAscent();
        final int fontDescent = fontMetrics.getDescent();
        final String[] split = text.split("\n");
        
        final int textHeight = split.length * fontHeight - fontDescent;
        final int top;
        switch(vAllignment)
        {
        default:
        case TOP:
            top = 0;
            break;
        case CENTER:
            top = (getHeigth() - textHeight) / 2;
            break;
        case BOTTOM:
            top = getHeigth() - textHeight;
            break;
        
        }
        
        int line = 0;
        for (String string : split)
        {
            final int stringWidth = fontMetrics.stringWidth(string);
            final int x;
            switch(hAllignment)
            {
            default:
            case LEFT:
                x = 0;
                break;
            case CENTER:
                x = (getWidth() - stringWidth) / 2;
                break;
            case RIGHT:
                x = getWidth() - stringWidth;
                break;
            }
            final int y = top + fontHeight * line + fontAscent;
            g.drawString(string, x, y);
            line++;
        }
    }
    
    @Override
    public Dimension getPreferedSize(Graphics2D g)
    {
        return getPreferedSize(g, font, text);
    }
    
    public static Dimension getPreferedSize(Graphics2D g, Font testFont, String testText)
    {
        if(g == null)
        {
            return new Dimension(100, 10);
        }
        g.setFont(testFont);
        final FontMetrics fontMetrics = g.getFontMetrics();
        final int fontHeight = fontMetrics.getHeight();
        final int fontDescent = fontMetrics.getDescent();
        final String[] split = testText.split("\n");
        int max = 0;
        for (String string : split)
        {
            final int stringWidth = fontMetrics.stringWidth(string);
            if (stringWidth > max)
                max = stringWidth;
        }
        return new Dimension(max, split.length * fontHeight - fontDescent);
    }
    
    public void fitFontSize(Graphics2D g, Dimension size)
    {
        final Dimension testSize = getPreferedSize(g);
        final float sx = (float)testSize.width / size.width;
        final float sy = (float)testSize.height / size.height;
        final float fontSize;
        if (sx > sy)
        {
            fontSize = getFont().getSize2D() / sx;
        }
        else
        {
            fontSize = getFont().getSize2D() / sy;
        }
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
