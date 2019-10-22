package de.klierlinge.clear19.widgets;

import java.awt.Dimension;
import java.awt.Font;
import java.awt.FontMetrics;
import java.awt.Graphics2D;
import java.util.Objects;

public class TextWidget extends Widget
{
    private String text;
    private TextAllignment textAllignment = TextAllignment.LEFT;
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
        final String[] split = text.split("\n");
        int line = 0;
        for (String string : split)
        {
            final int stringWidth = fontMetrics.stringWidth(string);
            final int x;
            switch(textAllignment)
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
            final int y = fontHeight * line + fontAscent;
            g.drawString(string, x, y);
            line++;
        }
    }

    @Override
    public Dimension getPreferedSize(Graphics2D g)
    {
        if(g == null)
        {
            return new Dimension(100, 10);
        }
        g.setFont(font);
        final FontMetrics fontMetrics = g.getFontMetrics();
        final int fontHeight = fontMetrics.getHeight();
        final int fontDescent = fontMetrics.getDescent();
        final String[] split = text.split("\n");
        int max = 0;
        for (String string : split)
        {
            final int stringWidth = fontMetrics.stringWidth(string);
            if (stringWidth > max)
                max = stringWidth;
        }
        return new Dimension(max, split.length * fontHeight - fontDescent);
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

    public TextAllignment getTextAllignment()
    {
        return textAllignment;
    }

    public void setTextAllignment(TextAllignment textAllignment)
    {
        if (this.textAllignment != textAllignment)
        {
            this.textAllignment = textAllignment;
            setDirty();
        }
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

    public enum TextAllignment
    {
        LEFT,
        CENTER,
        RIGHT
    }
}
