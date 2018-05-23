# coding: utf-8
#
""" Helper for draing"""
import PIL.Image as Img
import PIL.ImageDraw as Draw
import PIL.ImageFont as Font

class Frame(object):
    """docstring for Frame."""

    def __init__(self):
        super(Frame, self).__init__()
        self.__size_x = 320
        self.__size_y = 240
        self.__pixel_width = 2
        self.__map = [0] * (self.__size_x * self.__size_y * self.__pixel_width)

    def __get_column(self, column_i):
        """Get start point for column by column index"""
        return column_i * self.__size_y * self.__pixel_width

    def set_point(self, position, color):
        """Set pixel on map"""
        column = self.__get_column(position[0])
        index = column + position[1] * 2

        uint_16_color = self.__rgb_to_uint16(color)

        self.__map[index] = self.__value_low(uint_16_color)
        self.__map[index + 1] = self.__value_high(uint_16_color)

    def get_map(self):
        """Getter for map"""
        return self.__map

    @staticmethod
    def __value_high(value=0):
        return value & 0xff

    @staticmethod
    def __value_low(value=0):
        return value >> 8 & 0xff

    @staticmethod
    def __rgb_to_uint16(color_rgb):
        """Converts a RGB value to 16bit highcolor (5-6-5).

        @return 16bit highcolor value in little-endian.

        """
        red_bits = color_rgb[0] * 2**5 / 255
        green_bits = color_rgb[1] * 2**6 / 255
        blue_bits = color_rgb[2] * 2**5 / 255

        red_bits = red_bits if red_bits <= 0b00011111 else 0b00011111
        green_bits = green_bits if green_bits <= 0b00111111 else 0b00111111
        blue_bits = blue_bits if blue_bits <= 0b00011111 else 0b00011111

        value_high = (red_bits << 3) | (green_bits >> 3)
        value_low = (green_bits << 5) | blue_bits
        return value_low << 8 | value_high


class Drawer(object):
    """docstring for Drawer."""
    def __init__(self, frame):
        super(Drawer, self).__init__()
        self.__frame = frame

    def get_frame_data(self):
        """Getter for frame data"""
        return self.__frame.get_map()

    def draw_point(self, position, color_rgb):
        """Draw point on frame"""
        self.__frame.set_point(position, color_rgb)

    def draw_rectangle(self, position, size, color_rgb):
        """Draw rectangle on frame"""
        end_point_x = position[0] + size[0]
        end_point_y = position[1] + size[1]
        for pixel_x in xrange(position[0], end_point_x):
            for pixel_y in xrange(position[1], end_point_y):
                self.draw_point([pixel_x, pixel_y], color_rgb)

    def draw_line(self, position_start, position_end, color_rgb):
        """Draw line"""
        delta_y = position_end[1] - position_start[1]
        delta_x = position_end[0] - position_start[0]
        for offset_x in xrange(delta_x):
            offset_y = delta_y * offset_x / delta_x
            pixel_x = position_start[0] + offset_x
            pixel_y = position_start[1] + offset_y
            self.draw_point([pixel_x, pixel_y], color_rgb)

    def draw_image_from_file(self, filename, position, size):
        """Draw image frome file"""
        img = Img.open(filename)
        self.draw_image(img, position, size)

    def draw_image(self, img, position, size):
        """Draw image"""
        access = img.load()

        if img.size != (size[0], size[1]):
            img = img.resize((size[0], size[1]), Img.CUBIC)
            access = img.load()

        for pixel_x in range(size[0]):
            for pixel_y in range(size[1]):
                if len(access[pixel_x, pixel_y]) > 3:
                    alpha_channel = access[pixel_x, pixel_y][3]
                    if alpha_channel == 0:
                        continue
                color_rgb = access[pixel_x, pixel_y][0:3]
                pixel_position = [position[0] + pixel_x, position[1] + pixel_y]
                self.draw_point(pixel_position, color_rgb)

    def draw_text(self, position, font_size, text):
        """Draw text"""
        img = Img.new("RGBA", (320, 240), (0, 0, 0, 0))
        draw = Draw.Draw(img)
        font = Font.truetype("micradi.ttf", font_size)
        draw.text(position, text, (0, 0, 0), font=font)
        self.draw_image(img, [0, 0], [320, 240])




if __name__ == '__main__':
    print "Пошёл на хуй"
