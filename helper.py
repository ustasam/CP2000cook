# -*- coding: utf-8 -*-

import cp2000


def debug(value):
    return "dec=" + str(value) + ", bin=" + str(bin(int(value))) + ", hex=" + str(hex(int(value)))


def parse_time(time):
    n = time.strip(' \t\r\n').split(":")
    if len(n) == 0:
        return 0
    elif len(n) == 1:
        return int(n[0])
    elif len(n) == 2:
        return int(n[0]) * 60 + int(n[1])
    elif len(n) == 3:
        return int(n[0]) * 3600 + int(n[1]) * 60 + int(n[2])
    else:
        return 0


def parse_direction(direction):
    d = direction.strip(' \t\r\n').lover()
    if d in ["fwd", "forward", "вперед", "вп", "впер", "в", "1"]:
        return cp2000.Direction.FWD
    elif d in ["rev", "reverse ", "назад", "наз", "н", "2"]:
        return cp2000.Direction.REV
    else:
        return cp2000.Direction.UNKNOWN


def parse_freq(freq):
    f = freq.strip(' \t\r\n').lover()
    return float(f)


def default(value, default_value):
    if value is None:
        return default_value
    else:
        return value
