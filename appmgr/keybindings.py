# coding: utf-8
"""Key listener for G19 (only G19 just bucause of restrictions of original driver)"""
from logitech.g19_keys import (Data, Key)
# from logitech.g19_receivers import InputProcessor

class KeyBindings(object):
    '''Simple color changing.

    Enable M1..3 for red/green/blue and use the scroll to change the intensity
    for the currently selected colors.

    '''

    def __init__(self, lg19):
        self.__lg19 = lg19
        self.__cur_m = Data.LIGHT_KEY_M1

    def _update_leds(self):
        '''Updates M-leds according to enabled state.'''
        self.__lg19.set_enabled_m_keys(self.__cur_m)

    def __execute_macros(self, keys):
        """Execute macros which bind on pressed key"""
        pass

    def get_input_processor(self):
        """Getter"""
        return self

    def process_input(self, evt):
        """Handler for keyboard listener"""
        processed = False
        if Key.M1 in evt.keysDown:
            self.__cur_m = Data.LIGHT_KEY_M1
            processed = True
        if Key.M2 in evt.keysDown:
            self.__cur_m = Data.LIGHT_KEY_M2
            processed = True
        if Key.M3 in evt.keysDown:
            self.__cur_m = Data.LIGHT_KEY_M3
            processed = True

        self._update_leds()

        processed = processed or self.__execute_macros(evt.keysDown)

        return processed
