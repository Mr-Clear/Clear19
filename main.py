# coding: utf-8
"""Userspace driwer"""

from time import sleep
from logitech.g19 import G19
import libdraw

def main():
    """Main"""
    print 9 / 2
    g19_lcd = G19(True)
    frame = libdraw.Frame()
    drawer = libdraw.Drawer(frame)
    drawer.draw_rectangle([0, 0], [320, 240], [255, 255, 255])
    drawer.draw_rectangle([20, 20], [100, 100], [0, 0, 255])
    drawer.draw_rectangle([170, 120], [50, 50], [0, 0, 255])
    drawer.draw_image_from_file("/home/grayhook/Изображения/golovka.png", [170, 120], [150, 120])
    drawer.draw_text([40, 120], 32, u"ТЫ ПИДОР")

    g19_lcd.send_frame(drawer.get_frame_data())
    sleep(5)
    g19_lcd.reset()

if __name__ == '__main__':
    main()
