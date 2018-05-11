# -*- coding: utf-8 -*-
"""Defaults."""

import minimalmodbus
import serial
import logging

recipes_folder = "./recepies"

logfile = "cp2000.log"

PORT = '/dev/ttyUSB0'
ADDRESS = 1  # modbus instrument address

minimalmodbus.BAUDRATE = 9600
minimalmodbus.BYTESIZE = 7  # 7N2
minimalmodbus.PARITY = serial.PARITY_NONE
minimalmodbus.STOPBITS = 2
minimalmodbus.TIMEOUT = 0.1
minimalmodbus_mode = "ascii"  # rtu or ascii
minimalmodbus_debug = False

emulate_instrument = False

# device parameters
FREQ_CORRECTION = 40 / 38  # frequency correction

max_execution_time = 24 * 60 * 60  # 1 day
max_frequency = 1100
min_frequency = 1
direction_reverse_min_time = 1500  # ms

#

logLevel = logging.DEBUG

gladefile = "cp2000.glade"
