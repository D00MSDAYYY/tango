import numpy as np
from tango.server import run
from tango.server import Device
from tango.server import attribute, command
from collections import deque
from typing import Deque, List, Optional, Union, Tuple
from threading import Lock
import time


class Clock(Device):
    # fmt: off
    PULSE_MODE_POLLING_PERIOD_EPSILON_MS:int    = 5
    PULSE_MODE_EVENT_PERIOD_MS:int              = 1000
    PULSE_MODE_ARRAY_SIZE:int                   = int(PULSE_MODE_EVENT_PERIOD_MS / PULSE_MODE_POLLING_PERIOD_EPSILON_MS)
    PULSE_MODE_DUMMY_ARRAY: Deque[float]        = deque(maxlen=1000)
    # fmt: on
    # ########################################################################################
    # ########################################################################################
    _enable_pulse_mode: bool = False
    # ########################################################################################
    enable_pulse_mode = attribute(
        label="enable pulse mode", dtype=bool, doc="Pulse mode ON(1)/OFF(0) атрибут"
    )
    # ########################################################################################
    _prev_read_time: float = 0.0
    # ########################################################################################
    @enable_pulse_mode.read
    def _(self):
        return self._enable_pulse_mode

    # ########################################################################################
    @enable_pulse_mode.write
    def _(self, flag: bool):
        self._enable_pulse_mode = flag
        if self._enable_pulse_mode == True:
            self.poll_attribute(
                "_dont_ever_use_this_attribute_for_any_purpose",
                self.PULSE_MODE_POLLING_PERIOD_EPSILON_MS,
            )

    # ########################################################################################
    # ########################################################################################
    _pulse_mode_voltage_values_lock: Lock = Lock()
    # ########################################################################################
    _pulse_mode_voltage_values: Deque[float]
    # ########################################################################################
    pulse_mode_voltage_values = attribute(
        label="pulse_mode_voltage_values",
        dtype=[float],
        doc="атрибут, где хранится массив значений напряжений",
        period=1000,
    )
    # ########################################################################################
    @pulse_mode_voltage_values.read
    def _(self):
        if self._enable_pulse_mode:
            with self._pulse_mode_voltage_values_lock:
                result = list(self._pulse_mode_voltage_values)
                return result
        else:
            return self.PULSE_MODE_DUMMY_ARRAY
    # ########################################################################################
    # ########################################################################################
    _dont_ever_use_this_attribute_for_any_purpose = attribute(
        label="_dont_ever_use_this_attribute_for_any_purpose",
        dtype=str,
        doc="костыль, нужный для работы pulse mode. не подписывайтесь и не читайте его!!!",
    )
    # ########################################################################################
    _stash: Deque[float]
    # ########################################################################################
    @_dont_ever_use_this_attribute_for_any_purpose.read
    def _(self):
        cur_val = 0  # TODO insert logic for reading это должна быть одна и та же функция что и при чтении одномерного аттрибута
        self._stash.append(cur_val)
        if len(self._stash) >= self.PULSE_MODE_ARRAY_SIZE:
            with self._pulse_mode_voltage_values_lock:
                self._pulse_mode_voltage_values = (
                    self._stash
                )
                self._stash = deque()

    # ########################################################################################
    # ########################################################################################
    def init_device(self):
        super().init_device()

if __name__ == "__main__":
    run((Clock,))
