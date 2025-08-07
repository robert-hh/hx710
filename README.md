# HX710: Python class for the HX710 load cell

This is a very short and simple class. This lib includes three variants of the
module. One is using direct GPIO pin handling, the other uses the PIO
module of the RPI Pico. The third variant uses SPI.
Besides the class instantiation, all variants offer the same methods.
The preferred methods are GPIO and PIO, because they deal properly with the conversion
ready signal resulting in a more precise result.

## Constructor

### hx710 = HX710(clock_pin, data_pin, mode=1)

This is the GPIO constructor. `data_pin` and `clock_pin` are the pin objects
of the GPIO pins used for the communication. `clock_pin` must not be an input-only pin.
`mode` is the setting of the load cell amplifier.
The default value of 1 also selects the external sensor.

### hx710 = HX710(clock_pin, data_pin, mode=1, state_machine=0)

This is the Raspberry Pi PIO constructor. `data_pin` and `clock_pin` are the pin objects
of the GPIO pins used for the communication.
`mode` is the setting of the load cell amplifier.
The default value of 1 also selects the external sensor.
The argument `state_machine` can be set to different values if conflicting with
other uses, like if than one HX710 device is used by an application.

### hx710 = HX710(clock_pin, data_pin, spi, mode=1)

This is the SPI constructor. `data_pin` is the SPI MISO, `clock_pin` the SPI MOSI. These must be
Pin objects, with `data_pin` defined for input, `clock_pin` defined as output.
They must be supplied in addition to the spi object, even if spi uses
the same  pins for miso and mosi.
`spi` is the SPI object. The spi clock signal will not be be used.
`mode` is the of of the load cell amplifier.
The default value of 1 also selects the external sensor.

## Methods

### hx710.set_mode(mode)

Sets the mode which is used for the next call of hx710.read()

|Mode|Value|
|:-:|:-:|
|1|External Sensor at 10 Hz|
|2|Internal Temperature (HX710A)|
|2|DVDD - AVDD (HB710B)|
|3|External Sensor at 40 Hz|

### result = hx710.read()
### result = hx710()

Returns the actual raw value of the load cell. Raw means: not scaled, no offset
compensation.

### result = hx710.read_average(times=3)

Returns the raw value of the load cell as the average of `times` readings of The
raw value.

### result = hx710.read_lowpass()

Returns the actual value of the load cell fed through an one stage IIR lowpass
filter. The properties of the filter can be set with set_time_constant().

### rh = hx710.set_time_constant(value=None)

Set the time constant used by hx710.read_lowpass(). The range is 0-1.0. Smaller
values means longer times to settle and better smoothing.
If value is None, the actual value of the time constant is returned.

### value = hx710.get_value()

Returns the difference of the filtered load cell value and the offset, as set by hx710.set_offset() or hx710.tare()

### units = hx710.get_units()

Returns the value delivered by hx710.get_value() divided by the scale set by
hx710.set_scale().

### hx710.tare(times=15)

Determine the tare value of the load cell by averaging `times` raw readings.

### hx710.power_down()

Set the load cell to sleep mode.

### hx710.power_up()

Switch the load cell on again.

## Examples

```
# Example for Pycom device, gpio mode
# Connections:
# Pin # | HX710
# ------|-----------
# P9    | data_pin
# P10   | clock_pin
#

from hx710_gpio import HX710
from machine import Pin

pin_OUT = Pin("P9", Pin.IN, pull=Pin.PULL_DOWN)
pin_SCK = Pin("P10", Pin.OUT)

hx710 = HX710(pin_SCK, pin_OUT)

hx710.tare()
value = hx710.read()
value = hx710.get_value()
```

```
# Example for micropython.org device, gpio mode
# Connections:
# Pin # | HX710
# ------|-----------
# 12    | data_pin
# 13    | clock_pin
#

from hx710_gpio import HX710
from machine import Pin

pin_OUT = Pin(12, Pin.IN, pull=Pin.PULL_DOWN)
pin_SCK = Pin(13, Pin.OUT)

hx710 = HX710(pin_SCK, pin_OUT)

hx710.tare()
value = hx710.read()
value = hx710.get_value()
```

```
# Example for micropython.org device, RP2040 PIO mode
# Connections:
# Pin # | HX710
# ------|-----------
# 12    | data_pin
# 13    | clock_pin
#

from hx710_pio import HX710
from machine import Pin

pin_OUT = Pin(12, Pin.IN, pull=Pin.PULL_DOWN)
pin_SCK = Pin(13, Pin.OUT)

hx710 = HX710(pin_SCK, pin_OUT)

hx710.tare()
value = hx710.read()
value = hx710.get_value()
```

```
# Example for Pycom device, spi mode
# Connections:
# Pin # | HX710
# ------|-----------
# P9    | data_pin
# P10   | clock_pin
# None  | spi clock
#

from hx710_spi import HX710
from machine import Pin, SPI

pin_OUT = Pin("P9", Pin.IN, pull=Pin.PULL_DOWN)
pin_SCK = Pin("P10", Pin.OUT)

spi = SPI(0, mode=SPI.MASTER, baudrate=1000000, polarity=0,
             phase=0, pins=(None, pin_SCK, pin_OUT))

hx = HX710(pin_SCK, pin_OUT, spi)

hx710.tare()
value = hx710.read()
value = hx710.get_value()
```

```
# Example for micropython.org device, spi mode
# Connections:
# Pin # | HX710
# ------|-----------
# 12    | data_pin
# 13    | clock_pin
# 14    | spi clock

from hx710_spi import HX710
from machine import Pin

pin_OUT = Pin(12, Pin.IN, pull=Pin.PULL_DOWN)
pin_SCK = Pin(13, Pin.OUT)
spi_SCK = Pin(14)

spi = SPI(1, baudrate=1000000, polarity=0,
          phase=0, sck=spi_SCK, mosi=pin_SCK, miso=pin_OUT)

hx = HX710(pin_SCK, pin_OUT, spi)

hx710.tare()
value = hx710.read()
value = hx710.get_value()
```
