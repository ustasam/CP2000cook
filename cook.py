# -*- coding: utf-8 -*-

import logging
import time
import csv
from lark import Lark

import config
import helper
import cp2000 as dev
import dsl
import dialog


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


class Command(object):
    WAIT_OPERATOR = 1
    EXECUTE = 2
    UNKNOWN = 99

    @staticmethod
    def repr(command):
        if command == Command.WAIT_OPERATOR:
            return "Ожидание"
        elif command == Command.EXECUTE:
            return "Процесс"
        elif command == Command.UNKNOWN:
            return "Неизвестно"
        else:
            return "Неизвестно"


class CommandLine(object):
    NAME = 1
    MESSAGE = 2
    PAUSE = 3
    BEEP = 4
    RUN = 5
    STOP = 6
    END = 7

    @staticmethod
    def repr(command):
        if command == Command.WAIT_OPERATOR:
            return "Ожидание"
        elif command == Command.EXECUTE:
            return "Процесс"
        elif command == Command.UNKNOWN:
            return "Неизвестно"
        else:
            return "Неизвестно"


class Cook(object):

    def __init__(self, instrument=None):
        self.recipeName = ""
        self.recipeFile = ""
        self.commands = []
        self.position = 0

        self._state = State.UNKNOWN
        self._command = Command.UNKNOWN

        t = time.time()
        self.recipe_start_time = t
        self.recipe_end_time = t
        self.command_start_time = t
        self.command_end_time = t

        self.device = dev.CP2000(instrument)

        self.lark = Lark('''start: WORD "," WORD "!"
            %import common.WORD
            %ignore " "
            ''')

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
    def command(self):
        return self._command

    @command.setter
    def command(self, value):
        self._command = value

    @property
    def recipe_execution_time(self):
        return self.recipe_end_time - self.recipe_start_time

    @property
    def recipe_rest_time(self):
        return self.recipe_end_time - time.time()

    @property
    def command_execution_time(self):
        return self.command_end_time - self.command_start_time

    @property
    def command_rest_time(self):
        return self.command_end_time - time.time()

    @property
    def state_str(self):
        return State.repr(self.state)

    def end(self):
        self.device.stop()
        self.state = State.STOPPED

    def run(self):
        self.position = 0
        self.recipe_start_time = time.time()
        self.command_start_time = self.recipe_start_time
        self.state = State.RUNNING
        self.execute_line()
        logging.info("start_commands()")

    def resume(self):
        self.state = State.RUNNING
        self.execute_line()
        logging.info("resume_commands()")

    def tick(self):
        if self.state == State.MANUAL:
            self.manual_tick()
        elif self.state == State.RUNNING:
            self.program_tick()

    def manual_tick(self):
        if self.recipe_rest_time > 0:
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

    def manual_execute(self, direction=None, freq=1, execution_time=1, period=0):
        if not State.is_running(self.state):
            self.device.freq = freq
            self.device.direction = direction
            self.recipe_start_time = time.time()
            self.command_start_time = self.recipe_start_time
            self.recipe_end_time = self.recipe_start_time + min(execution_time, config.max_execution_time)
            if period == 0:
                self.command_end_time = self.recipe_end_time
            else:
                self.command_end_time = self.command_start_time + min(period, config.max_execution_time)
            self.state = State.MANUAL
            self.device.start()

    # --------------------------------------------------------------------------------------------------------

    def parse_command_line(self, textLine):
        commandLine = dict.fromkeys(['command', 'time', 'freq', 'message'])

        print(textLine)

        lines = csv.reader(
            textLine, quotechar='"', delimiter=' ',
            skipinitialspace=True)  # quoting=csv.QUOTE_ALL,
        items = []
        print(lines[0])
        if len(lines) == 1:
            items = lines[0]
        items.extend([None, None, None, None])
        commandLine.command = items[0].strip().lover()
        commandLine.time = float(items[1])
        commandLine.freq = float(items[2])
        commandLine.message = items[3].strip()
        return commandLine

    def get_current_command(self):
        textLine = self.recipeText[self.position]
        textLine = textLine.strip(' \t\r\n')
        commandLine = self.parse_command_line(textLine)
        return commandLine

    def execute_command(self):
        self.command_execution_start_time = time.time()
        if self.position >= len(self.recipeText):
            self.stop()
            logging.info("Execution complite.")
            return
        # cmd = get_current_command()

        # !!!!if cmd.command == "Пауза":
        # parse_line()

    def execute_next_command(self):
        self.position = self.position + 1
        self.execute_command()

    def recipeIsConfigLine(self, line):
        v = line.split('=', 1)
        if len(v) == 2:
            v_arg = v[0].strip(' \t\r\n\"').lower()
            v_value = v[1].strip(' \t\r\n\"')

            if v_arg == "name":
                self.recipeName = v_value
            elif v_arg == "conf_value_2":  # template
                self.conf2 = v_value

    def parse(self, text, gui_message=False, print_pretty=False):
        parse = None
        try:
            parse = dsl.parser.parse(text)
        except Exception as err:
            print("Error in recipe file.")
            print(err)
            if gui_message:
                dialog.infoDialog("Ошибка в разборе файла рецепта. \n" + str(err))
        if print_pretty and (parse is not None):
            print(parse.pretty())
            print(parse)

        return parse

    def readRecipe(self, recipe=""):

        self.recipeFile = recipe

        if recipe:
            with open(unicode(self.recipeFile, 'utf-8')) as f:

                text = unicode(f.read(), 'utf-8')

                p = self.parse(text, True, True)


                return

                self.recipeText = []
                for line in f:
                    line = line.strip(' \t\r\n')
                    if line != "":
                        self.parse_command_line(line)
                        #self.recipeText.append(line)
                        #self.recipeIsConfigLine(line)

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
