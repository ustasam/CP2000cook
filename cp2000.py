# -*- coding: utf-8 -*-

import minimalmodbus
import logging
import time

import config
import helper
import cp2000_constants as const


class CPState(object):
    STOPPED = const.REG_2000_F_STOP
    RUNNING = const.REG_2000_F_RUN

    @staticmethod
    def repr(state):
        if state == CPState.STOPPED:
            return "Остановлен"
        elif state == CPState.RUNNING:
            return "Запущен"
        else:
            return "Неизвестно"


class Direction(object):
    FWD = const.REG_2000_F_FWD
    REV = const.REG_2000_F_REV

    @staticmethod
    def repr(direction):
        if direction == Direction.FWD:
            return "Вперед"
        elif direction == Direction.REV:
            return "Назад"
        else:
            return "Неизвестно"


class CP2000(object):
    def __init__(self, instrument=None):
        self._freq = 1
        self._direction = Direction.FWD
        self._state = CPState.STOPPED
        self.instrument = instrument

    def write_reg(self, reg, value):
        if not config.emulate_instrument:
            try:
                self.instrument.write_register(reg, value)
            except (ValueError, IOError, Exception) as err:
                err_text = "write_reg(): Ошибка передачи данных modbus RS485."
                logging.error(str(err) + "\r\n" + err_text)

            logging.info("write_reg(): " + hex(reg) + ", value= " + helper.debug(value))
        else:
            logging.info("Emulated write_reg(): " + hex(reg) + ", value= " + helper.debug(value))

    def read_reg(self, reg):
        result = 0xFFFF
        if not config.emulate_instrument:
            try:
                result = self.instrument.read_register(reg)
            except (ValueError, IOError, Exception) as err:
                err_text = "read_reg(): Ошибка передачи данных modbus RS485."
                logging.error(str(err) + "\r\n" + err_text)

            logging.info("read_reg(): " + hex(reg) + ", value= " + helper.debug(result))
        else:
            logging.info("Emulated read_reg(): " + hex(reg))
        return result

    @property
    def state(self):
        return self._state

    @property
    def freq(self):
        return self._freq

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        value = helper.default(value, Direction.FWD)
        if self._direction != value:
            self._direction = value
            self.restart()
            logging.info("cp2000 set direction: " + str(self.direction))

    def reverse(self):
        if self.direction == Direction.FWD:
            self.direction = Direction.REV
        else:
            self.direction = Direction.FWD

    @freq.setter
    def freq(self, value):
        value = helper.default(value, 1)
        if self._freq != value:
            self._freq = value
            self.write_reg(const.REG_FREQUENCY, int(self.freq * 100 * config.frequency_correction))
            logging.info("cp2000 set freq: " + str(self.freq))

    @state.setter
    def state(self, value):
        value = helper.default(value, CPState.STOPPED)
        if self._state != value:
            self._state = value
            self.cp_err_reset()

            if value == CPState.STOPPED:
                cmd = const.REG_2000_F_SET0021 | const.REG_2000_F_STOP | self.direction
                self.write_reg(const.REG_2000, cmd)

            elif value == CPState.RUNNING:
                self.write_reg(const.REG_FREQUENCY, int(self.freq * 100 * config.frequency_correction))

                cmd = const.REG_2000_F_SET0021 | const.REG_2000_F_RUN | self.direction
                self.write_reg(const.REG_2000,  cmd)

            logging.info(
                "state(): freq=" + str(self.freq) +
                ", direction=" + Direction.repr(self.direction) +
                ", state=" + CPState.repr(value))

    def start(self):
        self.state = CPState.RUNNING

    def stop(self):
        self.state = CPState.STOPPED

    def restart(self, stoptime=None):
        _stoptime = helper.default(stoptime, config.direction_reverse_min_time / 1000)
        if self.state == CPState.RUNNING:
            self.state = CPState.STOPPED
            if _stoptime != 0:
                time.sleep(_stoptime)
            self.state = CPState.RUNNING
    # ----------------------------

    def cp_err_reset(self):
        if self.cp_error:
            self.write_reg(const.REG_2002, const.REG_2002_F_RESET)

    @property
    def cp_state(self):
        return self.read_reg(const.REG_STATE)

    @property
    def cp_ready(self):
        return self.cp_state & const.REG_STATE_F_SANDBY

    @property
    def cp_status(self):
        return self.read_reg(const.REG_Drive_Status)

    @property
    def cp_rotated(self):
        return self.cp_status & (const.REG_Drive_Status_Forward | const.REG_Drive_Status_Reverse)

    @property
    def cp_error(self):
        return self.cp_status & const.REG_Drive_Status_Error

    @property
    def cp_freq(self):
        return self.read_reg(const.REG_FREQUENCY_COMMAND)

    @property
    def cp_freq_current(self):
        return self.read_reg(const.REG_FREQUENCY_OUTPUT)

    @property
    def cp_speed(self):
        return self.read_reg(const.REG_Actual_Motor_Speed)

    @staticmethod
    def get_instrument(port, address, mode):
        try:
            inst = minimalmodbus.Instrument(port, address, mode)
            # inst.debug = config.minimalmodbus_debug
            inst.read_register(const.REG_FREQUENCY_COMMAND)
        except (ValueError, IOError, Exception) as err:
            logging.error("get_instrument(): " + "Ошибка соединение RS485 с контроллером CP2000. " + str(err))
            return None
        else:
            return inst


def cp2000_communication_test(instrument=None):
    time.sleep(0.1)
    logging.info("cp2000_communication_test()")

    if instrument is None:
        inst = CP2000.get_instrument(config.PORT, config.ADDRESS, config.minimalmodbus_mode)
    else:
        inst = instrument

    if inst is not None:
        logging.info("Соединение с контроллером CP2000 по RS485 установленно.")

        inst.debug = True

        result = inst.read_register(const.REG_FREQUENCY_COMMAND)
        logging.info("Read REG_FREQUENCY_COMMAND - " + helper.debug(result))

        inst.write_register(0x2002, 0b10)
        inst.write_register(0x2001, 100)  # Hz * 100 = Hz00

        inst.write_register(0x2000, 0b10011111110010)

        time.sleep(5)

        result = inst.read_register(0x2102)
        logging.info("Read 0x2102 - " + helper.debug(result))

        result = inst.read_register(0x2103)
        logging.info("Read 0x2103 - " + helper.debug(result))

        result = inst.read_register(0x210C)
        logging.info("Read 0x210C - " + helper.debug(result))

        inst.write_register(0x2000, 0b10011111101001)
        logging.info(hex(0x2000))

        inst.debug = config.minimalmodbus_debug
        if instrument is None:
            inst.serial.close()
        logging.info("cp2000_communication_test(): Выполнен.")
    else:
        logging.info("cp2000_communication_test(): Ошибка соединение RS485 с контроллером CP2000.")
