package de.klierlinge.clear19;

import java.awt.Dimension;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.Image;

import javax.swing.JPanel;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class ImagePanel extends JPanel 
{
    private static final long serialVersionUID = 1L;
    private static final Logger logger = LogManager.getLogger(ImagePanel.class.getName());
    private Image image;
    
    public ImagePanel()
    {
        setPreferredSize(new Dimension(320, 240));
    }
    
    @Override
    public void paintComponent(Graphics g1)
    {
        logger.trace("Painting image");
        super.paintComponents(g1);
        Graphics2D g = (Graphics2D)g1;
        g.drawImage(image, 0, 0, null);
    }

    public Image getImage()
    {
        return image;
    }

    public void setImage(Image image)
    {
        this.image = image;
        repaint();
    }
}
