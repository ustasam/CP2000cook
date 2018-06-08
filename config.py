# -*- coding: utf-8 -*-

"""Defaults."""

import minimalmodbus
import serial
import logging


def config_files(dir):
    global recipes_menu_file, report_file, logfile, data_dir

    data_dir = dir
    recipes_menu_file = dir + u"/recipe.menu"
    report_file = dir + u"/report.csv"
    logfile = dir + u"/recipe.log"


config_files("./data")  # data_dir


logLevel = logging.DEBUG
print_debug = False  # print debug messages


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
frequency_correction = 40 / 38
max_execution_time = 24 * 60 * 60 - 1  # 1 day
max_frequency = 1100
min_frequency = 1
direction_reverse_min_time = 100  # ms


gui_update_period = 250  # ms

gladefile = "cp2000.glade"
cssfile = "cp2000.css"

languge = 'ru'
codepage = "cp1251"
