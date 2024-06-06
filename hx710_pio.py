# MIT License

# Copyright (c) 2024 

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from machine import Pin, idle, Timer
import time
import rp2

class HX710:
    def __init__(self, clock, data, mode=1):
        self.clock = clock
        self.data = data
        self.clock.value(False)

        self.MODE = 0
        self.OFFSET = 0
        self.SCALE = 1

        self.time_constant = 0.25
        self.filtered = 0
        self.sm_timer = Timer()

        # create the state machine
        self.sm = rp2.StateMachine(0, self.hx711_pio, freq=1_000_000,
                                   sideset_base=self.clock, in_base=self.data,
                                   jmp_pin=self.data)
        self.set_mode(mode);


    @rp2.asm_pio(
        sideset_init=rp2.PIO.OUT_LOW,
        in_shiftdir=rp2.PIO.SHIFT_LEFT,
        autopull=False,
        autopush=False,
    )

    def hx711_pio():
        pull()              .side (0)   # get the number of clock cycles
        mov(x, osr)         .side (0)

        label("bitloop")
        nop()               .side (1)   # active edge
        nop()               .side (1)
        in_(pins, 1)        .side (0)   # get the pin and shift it in
        jmp(x_dec, "bitloop")  .side (0)   # test for more bits
        
        label("finish")
        push(block)         .side (0)   # no, deliver data and start over


    def set_mode(self, mode):
        if mode in (1, 2, 3):
            self.MODE = mode

        self.read()
        self.filtered = self.read()

    def conversion_done_cb(self, data):
        self.conversion_done = True
        data.irq(handler=None)

    def read(self):
        self.conversion_done = False
        self.data.irq(trigger=Pin.IRQ_FALLING, handler=self.conversion_done_cb)
        # wait for the device being ready
        for _ in range(500):
            if self.conversion_done == True:
                break
            time.sleep_ms(1)
        else:
            self.data.irq(handler=None)
            raise OSError("Sensor does not respond")
        # Feed the waiting state machine & get the data
        self.sm.active(1)  # start the state machine
        self.sm.put(self.MODE + 24 - 1)     # set pulse count 25-27, start
        result = self.sm.get() >> self.MODE # get the result & discard MODE bits
        self.sm.active(0)  # stop the state machine
        if result == 0x7fffffff:
            raise OSError("Sensor does not respond")

        # check sign
        if result > 0x7fffff:
            result -= 0x1000000

        return result

    def read_average(self, times=3):
        sum = 0
        for i in range(times):
            sum += self.read()
        return sum / times

    def read_lowpass(self):
        self.filtered += self.time_constant * (self.read() - self.filtered)
        return self.filtered

    def get_value(self):
        return self.read_lowpass() - self.OFFSET

    def get_units(self):
        return self.get_value() / self.SCALE

    def tare(self, times=15):
        self.set_offset(self.read_average(times))

    def set_scale(self, scale):
        self.SCALE = scale

    def set_offset(self, offset):
        self.OFFSET = offset

    def set_time_constant(self, time_constant = None):
        if time_constant is None:
            return self.time_constant
        elif 0 < time_constant < 1.0:
            self.time_constant = time_constant

    def power_down(self):
        self.clock.value(False)
        self.clock.value(True)

    def power_up(self):
        self.clock.value(False)
