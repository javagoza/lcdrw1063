# About the lcdrw1063 library

The lcdrw1063 library provides a Python RW1063 LCD I2C driver to be used with Raspberry PI.

It gives functions to quickly control what is displayed and how.

Supports only i2c wiring.

# Dependencies

smbus2: A drop-in replacement for smbus-cffi/smbus-python in pure Python
<code bash>
pip install smbus2
</code>

# Wiring Diagram

![MIDAS Display to Raspberry Pi 4 wiring Diagram](docs/MIDASDisplayRPiWiring.png)

# TODO

* Add digital port for controlling the Chip Select (CS) state from the library.
* Add a digital port to turn the LCD backlight on/off.
* Add configuration of number of columns and rows.
* Helper function for setting cursor at specifies row and column.
* Encapsulate private methods.
