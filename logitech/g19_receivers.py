from .g19_keys import (Data, Key)
from .runnable import Runnable

import logging
import threading
import time


class InputProcessor(object):
    '''Object to process key presses.'''

    def process_input(self, input_event):
        '''Processes given event.

        Should return as fast as possible.  Any time-consuming processing
        should be done in another thread.

        @param input_event Event to process.
        @return True if event was consumed, or False if ignored.

        '''
        return False


class InputEvent(object):
    '''Event created by a key press or release.'''

    def __init__(self, old_state, new_state, keys_down, keys_up):
        '''Creates an InputEvent.

        @param old_state State before event happened.
        @param new_state State after event happened.
        @param keys_down Keys newly pressed.
        @param keys_up Kys released by this event.

        '''
        self.old_state = old_state
        self.new_state = new_state
        self.keys_down = keys_down
        self.keys_up = keys_up


class State(object):
    '''Current state of keyboard.'''

    def __init__(self):
        self.__keys_down = set()

    def _data_to_keys_g_and_m(self, data):
        '''Converts a G/M keys data package to a set of keys defined as
        pressed by it.

        '''
        if len(data) != 4 or data[0] != 2:
            raise ValueError("not a multimedia key packet: " + str(data))
        empty = 0x400000
        cur_val = data[3] << 16 | data[2] << 8 | data[1]
        keys = []
        while cur_val != empty:
            found_a_key = False
            for val in list(Data.gmKeys.keys()):
                if val & cur_val == val:
                    cur_val ^= val
                    keys.append(Data.gmKeys[val])
                    found_a_key = True
            if not found_a_key:
                raise ValueError("incorrect g/m key packet: " +
                        str(data))

        return set(keys)

    def _data_to_keys_mm(self, data):
        '''Converts a multimedia keys data package to a set of keys defined as
        pressed by it.

        '''
        if len(data) != 2 or data[0] not in [1, 3]:
            raise ValueError("not a multimedia key packet: " + str(data))
        if data[0] == 1:
            cur_val = data[1]
            keys = []
            while cur_val:
                found_a_key = False
                for val in list(Data.mmKeys.keys()):
                    if val & cur_val == val:
                        cur_val ^= val
                        keys.append(Data.mmKeys[val])
                        found_a_key = True
                if not found_a_key:
                    raise ValueError("incorrect multimedia key packet: " +
                            str(data))
        elif data == [3, 1]:
            keys = [Key.WINKEY_SWITCH]
        elif data == [3, 0]:
            keys = []
        else:
            raise ValueError("incorrect multimedia key packet: " + str(data))

        return set(keys)

    def _update_keys_down(self, possible_keys, keys):
        '''Updates internal keys_down set.

        Updates the current state of all keys in 'possibleKeys' with state
        given in 'keys'.

        Example:
        Currently set as pressed in self.__keysDown: [A, B]
        possibleKeys: [B, C, D]
        keys: [C]

        This would set self.__keysDown to [A, C] and return ([C], [B])

        @param possible_keys Keys whose state could be given as 'pressed' at the
        same time by 'keys'.
        @param keys Current state of all keys in possibleKeys.
        @return A pair of sets listing newly pressed and newly released keys.

        '''
        keys_down = set()
        keys_up = set()
        for key in possible_keys:
            if key in keys:
                if key not in self.__keys_down:
                    self.__keys_down.add(key)
                    keys_down.add(key)
            else:
                if key in self.__keys_down:
                    self.__keys_down.remove(key)
                    keys_up.add(key)
        return (keys_down, keys_up)

    def clone(self):
        '''Returns an exact copy of this state.'''
        state = State()
        state.__keys_down = set(self.__keys_down)
        return state

    def packet_received_g_and_m(self, data):
        '''Mutates the state by given data packet from G- and M- keys.

        @param data Data packet received.
        @return InputEvent for data packet, or None if data packet was ignored.

        '''
        old_state = self.clone()
        evt = None
        if len(data) == 4:
            keys = self._data_to_keys_g_and_m(data)
            keys_down, keys_up = self._update_keys_down(Key.gm_keys, keys)
            new_state = self.clone()
            evt = InputEvent(old_state, new_state, keys_down, keys_up)
        return evt

    def packet_received_mm(self, data):
        '''Mutates the state by given data packet from multimedia keys.

        @param data Data packet received.
        @return InputEvent for data packet.

        '''
        old_state = self.clone()
        if len(data) != 2:
            raise ValueError("incorrect multimedia key packet: " + str(data))
        keys = self._data_to_keys_mm(data)
        win_key_set = {Key.WINKEY_SWITCH}
        if data[0] == 1:
            # update state of all mm keys
            possible_keys = Key.mm_keys.difference(win_key_set)
            keys_down, keys_up = self._update_keys_down(possible_keys, keys)
        else:
            # update winkey state
            keys_down, keys_up = self._update_keys_down(win_key_set, keys)
        new_state = self.clone()
        return InputEvent(old_state, new_state, keys_down, keys_up)


class G19Receiver(Runnable):
    '''This receiver consumes all data sent by special keys.'''

    def __init__(self, g19):
        Runnable.__init__(self)
        self.__g19 = g19
        self.__ips = []
        self.__mutex = threading.Lock()
        self.__state = State()

    def add_input_processor(self, processor):
        '''Adds an input processor.'''
        self.__mutex.acquire()
        self.__ips.append(processor)
        self.__mutex.release()

    def execute(self):
        got_data = False
        processors = self.list_all_input_processors()

        # data = self.__g19.read_multimedia_keys()
        # if data:
        #     evt = self.__state.packet_received_mm(data)
        #     if evt:
        #         for proc in processors:
        #             if proc.process_input(evt):
        #                 break
        #     else:
        #         logging.debug("mm ignored: ", data)
        #     got_data = True

        data = self.__g19.read_g_and_m_keys()
        if data:
            evt = self.__state.packet_received_g_and_m(data)
            if evt:
                for proc in processors:
                    if proc.process_input(evt):
                        break
            else:
                logging.debug("m/g ignored: %s", data)
            got_data = True

        data = self.__g19.read_display_menu_keys()
        if data:
            logging.debug("dis: %s", data)
            got_data = True

        if not got_data:
            time.sleep(0.03)

    def list_all_input_processors(self):
        '''Returns a list of all input processors currently registered to this
        receiver.

        @return All registered processors.  This list is a copy of the internal
        one.

        '''
        self.__mutex.acquire()
        all_processors = list(self.__ips)
        self.__mutex.release()
        return all_processors
