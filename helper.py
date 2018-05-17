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


def parse_time2(ctime):  # yet another variant ;)
    items = ctime.split(":")[::-1]
    m = [1, 60, 3600, 3600 * 24]
    result = 0
    for i, item in enumerate(items):
        result += int(item) * m[i]
    return result


def parse_direction(direction):
    d = direction.strip(' \t\r\n').lover()
    if d in [True, "fwd", "forward", "вперед", "вп", "впер", "в", "1"]:
        return cp2000.Direction.FWD
    elif d in [False, "rev", "reverse ", "назад", "наз", "н", "2"]:
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


try:
    import winsound
except ImportError:
    import os

    def playsound(frequency, duration):
        # apt-get install beep
        os.system('beep -f %s -l %s' % (frequency, duration))
else:

    def playsound(frequency, duration):
        winsound.Beep(frequency, duration)
