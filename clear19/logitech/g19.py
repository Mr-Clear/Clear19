from __future__ import annotations

import logging
import threading
from enum import Enum
from threading import Lock
from typing import Set, List, Optional

import usb
from usb import Device

from clear19.widgets.geometry import Size

log = logging.getLogger(__name__)


class G19Key(Enum):
    pass


class DisplayKey(G19Key):
    SETTINGS = 0x01
    BACK = 0x02
    MENU = 0x04
    OK = 0x08
    RIGHT = 0x10
    LEFT = 0x20
    DOWN = 0x40
    UP = 0x80

    @staticmethod
    def get_display_keys(key_code: int) -> List[DisplayKey]:
        keys = []
        for key in DisplayKey:
            if key_code & key.value > 0:
                keys.append(key)
        return keys


class GKey(G19Key):
    G01 = 0x000001
    G02 = 0x000002
    G03 = 0x000004
    G04 = 0x000008
    G05 = 0x000010
    G06 = 0x000020
    G07 = 0x000040
    G08 = 0x000080
    G09 = 0x000100
    G10 = 0x000200
    G11 = 0x000400
    G12 = 0x000800
    M1 = 0x001000
    M2 = 0x002000
    M3 = 0x004000
    MR = 0x008000
    LIGHT = 0x080000

    @staticmethod
    def get_g_keys(key_code: int) -> List[GKey]:
        keys = []
        for key in GKey:
            if key_code & key.value > 0:
                keys.append(key)
        return keys


class KeyLight(Enum):
    M1 = 0x80
    M2 = 0x40
    M3 = 0x20
    MR = 0x10

    @staticmethod
    def set_to_code(s: Set) -> int:
        code = 0
        for v in s:
            code |= v.value
        return code


class G19(object):
    """Simple access to Logitech G19 features.

    All methods are thread-safe if not denoted otherwise.

    """

    _usb_device: G19UsbController
    _usb_device_mutex: Lock
    _interrupt: bool = False

    def __init__(self, reset_on_start=False):
        """Initializes and opens the USB device."""
        self._usb_device = G19UsbController(reset_on_start)
        self._usb_device_mutex = threading.Lock()

    @property
    def image_size(self) -> Size:
        return Size(320, 240)

    def set_interrupt(self):
        self._interrupt = True

    def unset_interrupt(self):
        self._interrupt = False

    def read_g_and_m_keys(self, max_len=20):
        """Reads interrupt data from G, M and light switch keys.

        @return maxLen Maximum number of bytes to read.
        @return Read data or empty list.

        """
        self._usb_device_mutex.acquire()
        val = []
        try:
            val = list(self._usb_device.handle_if_1.interruptRead(
                0x83, max_len, 10))
        except usb.USBError:
            pass
        finally:
            self._usb_device_mutex.release()
        return val

    def read_display_menu_keys(self):
        """Reads interrupt data from display keys.

        @return Read data or empty list.

        """
        self._usb_device_mutex.acquire()
        val = []
        try:
            val = list(self._usb_device.handle_if_0.interruptRead(0x81, 2, 10))
        except usb.USBError:
            pass
        finally:
            self._usb_device_mutex.release()
        return val

    def reset(self):
        """Initiates a bus reset to USB device."""
        self._usb_device_mutex.acquire()
        try:
            self._usb_device.reset()
        finally:
            self._usb_device_mutex.release()

    def save_default_bg_color(self, r, g, b):
        """This stores given color permanently to keyboard.

        After a reset this will be color used by default.

        """
        rtype = usb.TYPE_CLASS | usb.RECIP_INTERFACE
        color_data = [7, r, g, b]
        self._usb_device_mutex.acquire()
        try:
            self._usb_device.handle_if_1.controlMsg(
                rtype, 0x09, color_data, 0x308, 0x01, 1000)
        finally:
            self._usb_device_mutex.release()

    def send_frame(self, data):
        """Sends a frame to display.

        @param data 320x240x2 bytes, containing the frame in little-endian
        16bit highcolor (5-6-5) format.
        Image must be row-wise, starting at upper left corner and ending at
        lower right.  This means (data[0], data[1]) is the first pixel and
        (data[239 * 2], data[239 * 2 + 1]) the lower left one.

        """
        if self._interrupt:
            return
        if len(data) != (self.image_size.width * self.image_size.height * 2):
            raise ValueError("illegal frame size: " + str(len(data))
                             + " should be 320x240x2=" + str(self.image_size.width * self.image_size.height * 2))
        frame = bytearray([0x10, 0x0F, 0x00, 0x58, 0x02, 0x00, 0x00, 0x00,
                           0x00, 0x00, 0x00, 0x3F, 0x01, 0xEF, 0x00, 0x0F])
        for i in range(16, 256):
            frame.append(i)
        for i in range(256):
            frame.append(i)

        frame += data

        self._usb_device_mutex.acquire()
        try:
            self._usb_device.handle_if_0.bulkWrite(2, frame, 1000)
        except usb.USBError as err:
            log.error(f"USB error.", exc_info=True)
        finally:
            self._usb_device_mutex.release()

    def set_bg_color(self, r, g, b):
        """Sets backlight to given color."""
        rtype = usb.TYPE_CLASS | usb.RECIP_INTERFACE
        color_data = [7, r, g, b]
        self._usb_device_mutex.acquire()
        try:
            self._usb_device.handle_if_1.controlMsg(rtype, 0x09, color_data, 0x307, 0x01, 10)
        finally:
            self._usb_device_mutex.release()

    def set_enabled_m_keys(self, keys: Set[KeyLight]):
        """Sets currently lit keys as an OR-combination of LIGHT_KEY_M1..3,R.

        example:
            from logitech.g19_keys import Data
            lg19 = G19()
            lg19.set_enabled_m_keys(Data.LIGHT_KEY_M1 | Data.LIGHT_KEY_MR)

        """
        rtype = usb.TYPE_CLASS | usb.RECIP_INTERFACE
        self._usb_device_mutex.acquire()
        try:
            self._usb_device.handle_if_1.controlMsg(
                rtype, 0x09, [5, KeyLight.set_to_code(keys)], 0x305, 0x01, 10)
        finally:
            self._usb_device_mutex.release()

    def set_display_brightness(self, val):
        """Sets display brightness.

        @param val in [0,100] (off..maximum).

        """
        data = [val, 0xe2, 0x12, 0x00, 0x8c, 0x11, 0x00, 0x10, 0x00]
        rtype = usb.TYPE_VENDOR | usb.RECIP_INTERFACE
        self._usb_device_mutex.acquire()
        try:
            self._usb_device.handle_if_1.controlMsg(rtype, 0x0a, data, 0x0, 0x0)
        finally:
            self._usb_device_mutex.release()


class G19UsbController(object):
    """Controller for accessing the G19 USB device.

    The G19 consists of two composite USB devices:
        * 046d:c228
          The keyboard consisting of two interfaces:
              MI00: keyboard
                  EP 0x81(in)  - INT the keyboard itself
              MI01: (ifaceMM)
                  EP 0x82(in)  - multimedia keys, incl. scroll and Windows-key-switch

        * 046d:c229
          LCD display with two interfaces:
              MI00 (0x05): (iface0) via control data in: display keys
                  EP 0x81(in)  - INT
                  EP 0x02(out) - BULK display itself
              MI01 (0x06): (iface1) back light
                  EP 0x83(in)  - INT G-keys, M1..3/MR key, light key

    """
    _lcd_device: Optional[Device]
    _kbd_device: Optional[Device]

    def __init__(self, reset_on_start=False):
        self._lcd_device = self._find_device(0x046d, 0xc229)
        if not self._lcd_device:
            raise usb.USBError("G19 LCD not found on USB bus")
        self._kbd_device = self._find_device(0x046d, 0xc228)
        if not self._kbd_device:
            raise usb.USBError("G19 keyboard not found on USB bus")
        self.handle_if_0 = self._lcd_device.open()
        if reset_on_start:
            self.handle_if_0.reset()
            self.handle_if_0 = self._lcd_device.open()

        self.handle_if_1 = self._lcd_device.open()

        config = self._lcd_device.configurations[0]
        iface0 = config.interfaces[0][0]
        iface1 = config.interfaces[0][1]

        try:
            self.handle_if_1.detachKernelDriver(iface1)
        except usb.USBError:
            pass

        self.handle_if_0.setConfiguration(1)
        self.handle_if_1.setConfiguration(1)
        self.handle_if_0.claimInterface(iface0)
        self.handle_if_1.claimInterface(iface1)

    @staticmethod
    def _find_device(id_vendor, id_product) -> Optional[Device]:
        for bus in usb.busses():
            for dev in bus.devices:
                if dev.idVendor == id_vendor and \
                        dev.idProduct == id_product:
                    return dev
        return None

    def reset(self):
        """Resets the device on the USB."""
        self.handle_if_0.reset()
        self.handle_if_1.reset()
