# -*- coding: utf-8 -*-

import logging
import time
from lark import Lark, Tree

import config
import helper
import cp2000 as dev
import dsl


class State(object):
    STOPPED =  0b011110000
    RUNNING =       0b1111
    PROGRAM =       0b0001
    MANUAL =        0b0010
    COMPLETED = 0b00010000
    UNKNOWN =  0b100000000

    @staticmethod
    def is_running(state):
        return (State.RUNNING & state) != 0

    @staticmethod
    def is_stopped(state):
        return not State.is_running(state)

    @staticmethod
    def is_manual(state):
        return (State.MANUAL & state) != 0

    @staticmethod
    def is_program(state):
        return (State.PROGRAM & state) != 0

    @staticmethod
    def repr(state):
        if state == State.STOPPED:
            return "Остановлен"
        elif state == State.RUNNING:
            return "Запущен"
        elif state == State.PROGRAM:
            return "Программа"
        elif state == State.MANUAL:
            return "Ручной"
        elif state == State.COMPLETED:
            return "Выполнено"
        elif state == State.UNKNOWN:
            return "Неизвестно"
        else:
            return "Неизвестно"


class Cook(object):

    def __init__(self, instrument=None):
        self.recipeName = ""

        self.recipeFile = ""
        self.program = None

        self.current_command = None

        self.identifiers = {}

        # execution state
        self._state = State.STOPPED

        t = time.time()
        self.start_time = t
        self.end_time = t
        self.command_start_time = t
        self.command_end_time = t

        self.device = dev.CP2000(instrument)

    def cp_start(self, freq=None, direction=None):
        self.device.state = dev.CPState.STOPPED
        self.device.freq = helper.default(freq, self.device.freq)
        self.device.direction = helper.default(direction, self.device.direction)
        self.device.state = dev.CPState.RUNNING
        logging.info("start(): " + str(self.device.freq) + " " + dev.Direction.repr(self.device.direction))

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    @property
    def state_repr(self):
        return State.repr(self.state)

    @property
    def execution_time(self):
        return self.end_time - self.start_time

    @property
    def rest_time(self):
        return self.end_time - time.time()

    @property
    def command_execution_time(self):
        return self.command_end_time - self.command_start_time

    @property
    def command_rest_time(self):
        return self.command_end_time - time.time()

    @property
    def is_command_complete(self):
        return self.command_rest_time <= 0

    def compete_command(self):
        if not self.is_command_complete:
            self.command_end_time = time.time()

    def attr(self, node, position, default=None):
        if len(node.children) > position:
            return node.children[position].value
        return default

    def attr_i(self, node, position, default=0):
        result = int(self.attr(node, position, default))
        print "v " + str(result)
        return result

    def next_command(self):
        cmd = self.current_command
        if cmd.next:
            self.current_command = cmd.next
        else:
            if hasattr(cmd, 'parent'):
                self.current_command = cmd.parent
            else:
                self.current_command = None

    def execute(self, node, verify_only=False):
        # 22#self.current = node
        self.command_start_time = time.time()
        self.command_end_time = self.command_start_time

        try:
            if node.data == "program_name":
                self.recipeName = self.attr(node, 0, "")
                logging.info("% " + node.data + " " + self.recipeName)

            elif node.data == "beep":
                sound_freq = self.attr_i(node, 0, 3000)
                duration = self.attr_i(node, 1, 1000)
                times = self.attr_i(node, 2, 1)
                pause_length = self.attr_i(node, 3, 1000)

                if not verify_only:
                    for i in range(times):
                        helper.playsound(sound_freq, duration)
                        if i < (times - 1):
                            time.sleep(pause_length / 1000)
                    logging.info("% " + node.data + " " + sound_freq)

            elif node.data == "pause":
                if not verify_only:
                    logging.info("% " + node.data)

            elif node.data == "end":
                if not verify_only:
                    self.end()
                    logging.info("% " + node.data)

            elif node.data == "parameter":
                if not verify_only:
                    self.identifiers[self.attr(node, 0, "default")] = self.attr(node, 0, 3000)  # &&&???
                    logging.info("% " + node.data)

            elif node.data == "message":
                if not verify_only:
                    logging.info("% " + node.data)

            elif node.data == "repeat":
                if not verify_only:
                    logging.info("% " + node.data)

            elif node.data == "expression":
                if not verify_only:
                    logging.info("% " + node.data)

            elif node.data == "operate":
                if not verify_only:
                    logging.info("% " + node.data)

        except Exception as err:
            logging.info("Error execute() command: " + node.data + " " + str(err))

        for i in node.children:
            if isinstance(i, Tree):
                self.execute(i, verify_only)

    def end(self):
        self.device.stop()
        self.state = State.STOPPED
        logging.info("end()")

    def run(self):  # program_execute
        if not State.is_running(self.state):

            self.state = State.RUNNING
            self.start_time = time.time()
            logging.info("run()")

            self.current_command = self.program
            self.execute(self.program, True)
#            self.execute(self.program)

    def resume(self):
        if State.is_running(self.state):
            return
        self.state = State.RUNNING
        logging.info("resume()")

    def program_tick(self):
        pass

    def tick(self):
        if self.state == State.MANUAL:
            self.manual_tick()
        elif self.state == State.RUNNING:
            self.program_tick()

    def manual_tick(self):
        if self.rest_time > 0:
            if self.command_rest_time > 0:
                pass
            else:
                end_time = self.command_end_time
                self.command_end_time = self.command_end_time + (self.command_end_time - self.command_start_time)
                self.command_start_time = end_time
                self.device.direction_reverse()
        else:
            self.end()
            self.state == State.COMPLETED
            logging.info("manual completed")

    def manual_execute(self, direction=None, freq=1, execution_time=1, period=0):
        logging.info("manual_execute()")
        if not State.is_running(self.state):
            self.device.freq = freq
            self.device.direction = direction
            self.start_time = time.time()
            self.command_start_time = self.start_time
            self.end_time = self.start_time + min(execution_time, config.max_execution_time)
            if period == 0:
                self.command_end_time = self.end_time
            else:
                self.command_end_time = self.command_start_time + min(period, config.max_execution_time)
            self.state = State.MANUAL
            self.device.start()

    def readRecipe(self, recipe=""):
        if recipe:
            self.recipeFile = recipe
        with open(unicode(self.recipeFile, 'utf-8')) as f:

            text = unicode(f.read(), 'utf-8')
            self.program = dsl.parse_recipe_text(text, True, True)
            dsl.transform(self.program)

    # --------------------------------------------------------------------------------------------------------

    def reaction_test2(self):
        if not State.is_running(self.state):
            logging.info("reaction_test2(): Begin.")
            self.cp_start(2, dev.Direction.FWD)
            time.sleep(3)
            self.device.stop()
            time.sleep(1)
            self.cp_start(4, dev.Direction.REV)
            time.sleep(3)
            self.device.stop()
            logging.info("reaction_test2(): Complete.")
