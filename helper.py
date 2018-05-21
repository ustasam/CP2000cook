# -*- coding: utf-8 -*-

import cp2000
import config


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


def format_time(seconds):
    result = ""
    days = seconds // (3600 * 24)
    if days:
        result += "%d:" % days
    rest = seconds % (3600 * 24)
    hours = rest // 3600
    if hours + days:
        result += "%02d:" % hours
    rest = rest % 3600
    minutes = rest // 60
    if minutes + hours + days:
        result += "%02d:" % minutes
    seconds = rest % 60
    result += "%02d" % seconds
    return result


def parse_direction(direction):
    if type(direction) == str or type(direction) == unicode:
        d = unicode(direction.strip(' \t\r\n').lower())
    else:
        d = direction
    if d in [cp2000.Direction.FWD, True, 1, u"fwd", u"forward", u"вперед", u"вп", u"впер", u"в", u"1"]:
        return cp2000.Direction.FWD

    elif d in [cp2000.Direction.REV, False, 0, u"rev", u"reverse", u"назад", u"наз", u"н", u"2", u"0"]:
        return cp2000.Direction.REV

    else:
        return cp2000.Direction.UNKNOWN

#
# def parse_freq(freq):
#     f = freq.strip(' \t\r\n').lover()
#     return float(f)


def default(value, default_value):
    if value is None:
        return default_value
    else:
        return value


def console(message):
    print(message.encode(config.codepage))


def unicode_escape(value):
    value = unicode(value)
    return value.decode('raw_unicode_escape')


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
