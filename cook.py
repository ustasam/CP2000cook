# -*- coding: utf-8 -*-

import logging
import time
from lark import Tree
import threading
import os

import config
import helper
import cp2000 as dev
import dsl
import messages
import dialog


class State(object):
    STOPPED =  0b011110000
    RUNNING =       0b1111
    PROGRAM =       0b0001
    MANUAL =        0b0010
    SUSPEND =       0b0100
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
            return u"Остановлен"
        elif state == State.RUNNING:
            return u"Выполняется"
        elif state == State.PROGRAM:
            return u"Программа"
        elif state == State.MANUAL:
            return u"Ручной"
        elif state == State.COMPLETED:
            return u"Выполнено"
        elif state == State.UNKNOWN:
            return u"Неизвестно"
        else:
            return u"Неизвестно"


def paused(pause):
    return not pause.is_set()


def pause(pause, state=True):
    if state:
        pause.clear()
    else:
        pause.set()


class Cook(object):

    def __init__(self, instrument=None):

        self.recipeName = ""
        self.recipeFile = ""
        self.program = None

        self.command = None  # node of current command

        self.identifiers = {}
        self.errors = []

        self.message = ""

        self.pause = threading.Event()  # is_set() == False = pause
        self.user_pause = threading.Event()
        self.user_interaction = threading.Event()

        # execution state
        self._state = State.STOPPED

        self.start_time = time.time()
        self.end_time = time.time() - 1
        self.command_start_time = time.time()
        self.command_end_time = time.time() - 1

        self.device = dev.CP2000(instrument)

        self.lock = threading.Lock()

    def cp_start(self, freq=None, direction=None):
        self.lock.acquire()

        self.device.state = dev.CPState.STOPPED
        self.device.freq = helper.default(freq, self.device.freq)
        self.device.direction = helper.default(direction, self.device.direction)
        self.device.state = dev.CPState.RUNNING
        logging.info(u"start(): " + unicode(self.device.freq) + " " + dev.Direction.repr(self.device.direction))

        self.lock.release()

    @property
    def name(self):
        if self.recipeName:
            return self.recipeName
        elif self.recipeFile:
            return os.path.splitext(os.path.basename(self.recipeFile))[0]
        else:
            return ""

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
    def is_running(self):
        return State.is_running(self.state)

    @property
    def is_stopped(self):
        return State.is_stopped(self.state)

    #
    @property
    def time(self):
        return time.time() - self.start_time

    @property
    def total_time(self):
        return self.end_time - self.start_time

    @property
    def rest_time(self):
        return max(0, self.end_time - time.time())

    @property
    def command_time(self):
        return time.time() - self.command_start_time

    @property
    def command_total_time(self):
        return self.command_end_time - self.command_start_time

    @property
    def command_rest_time(self):
        return max(0, self.command_end_time - time.time())

    def stop(self):
        self.lock.acquire()
        self.state = State.STOPPED
        self.device.stop()
        self.lock.release()

        pause(self.user_interaction, False)
        pause(self.user_pause, False)
        pause(self.pause, False)
        logging.info(u"stop()")

    def pause_sleep(self, max_duration=2147483647, release_lock=False):

        begin_time = time.time()
        max_time = begin_time + max_duration

        lock_on_return = False
        if release_lock and self.lock.locked():
            lock_on_return = True
            self.lock.release()

        while (paused(self.pause) or paused(self.user_pause) or paused(self.user_interaction)) \
                and self.is_running:

            self.pause.wait(0.2)
            self.user_pause.wait(0.5)
            self.user_interaction.wait(0.5)

            if (max_time <= time.time()):
                pause(self.pause, False)

        if lock_on_return:
            self.lock.acquire()

        return time.time() - begin_time

    def expression(self, node):
        if node.data == "mul":
            return float(self.expression(node.children[0])) \
                * float(self.expression(node.children[1]))
        elif node.data == "div":
            return float(self.expression(node.children[0])) \
                / float(self.expression(node.children[1]))
        elif node.data == "add":
            return float(self.expression(node.children[0])) \
                + float(self.expression(node.children[1]))
        elif node.data == "sub":
            return float(self.expression(node.children[0])) \
                - float(self.expression(node.children[1]))
        elif node.data == "neg":
            return -1 * float(self.expression(node.children[0]))
        elif node.data == "constant":
            return node.children[0].value
        elif node.data == "identifier":
            identifier = unicode(node.children[0].value)
            if identifier in self.identifiers:
                return self.identifiers[identifier]
            else:
                self.errors.append(["error", "expression", u"Identifier %s not fount." % identifier])
                return 0

    def eval(self, node, verification=False):

        self.pause_sleep()

        if not self.is_running:
            return

        self.command = node
        name = self.command.data
        self.command.name = name
        self.command.loc_name = dsl.get_command_loc_name(self.command.name)

        args = dsl.get_command_arguments(self.command)
        args = dsl.fill_identifiers(args, self.identifiers)
        self.command.args = args

        self.command_start_time = time.time()
        self.command_end_time = self.command_start_time

        if config.print_debug:
            helper.console(u"\n" + "-" * 10 + helper.unicode_escape(node.data) + "-"*10)
            helper.console(u"self.identifiers=" + helper.unicode_escape(self.identifiers))
            helper.console(u"self.command=" + helper.unicode_escape(self.command))
            helper.console(u"self.command.args=" + helper.unicode_escape(self.command.args))

        logging.info(u"% " + name + " " + helper.unicode_escape(args))

#        try:
        if 1 == 1:
            if name == "program_name":
                self.recipeName = args['name']
                if self.recipeName == "":
                    self.errors.append(["warinig", name, u"Program name is blank."])

            elif name == "end":

                self.stop()
                self.state = State.COMPLETED

                self.lock.acquire()
                self.device.stop()
                self.lock.release()

            elif name == "stop":
                self.lock.acquire()
                self.device.stop()
                self.lock.release()

            elif name == "message":
                self.message = args['message']

            elif name == "message_dialog":
                if not verification:

                    self.message = args['message']

                    pause(self.user_interaction)
                    self.user_interaction.wait()

            elif name == "input":
                if not verification:

                    pause(self.user_interaction)
                    self.user_interaction.wait()

                    if type(args['default']) == str or type(args['default']) == unicode:
                        self.identifiers[args['name']] = self.command.result
                    else:
                        self.identifiers[args['name']] = float(self.command.result)

            elif name == "wait":
                if not verification:

                    pause(self.pause)
                    self.pause_sleep(max_duration=args['duration'])
                    pause(self.pause, False)

            elif name == "beep":
                if not verification:

                    for i in range(args['count']):

                        helper.playsound(args['frequency'], args['duration'] * 1000)
                        if i < (args['count'] - 1):
                            time.sleep(args['pause'])

                else:
                    duration = (args['duration'] * args['count'] + args['pause'] * (args['count'] - 1))
                    if duration > 15:
                        self.errors.append(["warinig", name,
                                            u"Beep duration too long: " + helper.unicode_escape(duration)])

            elif name == "repeat":

                current_command = self.command
                for i in range(args['count']):
                    for code_block_node in current_command.children:
                        if isinstance(code_block_node, Tree):
                            for cmd in code_block_node.children:
                                if isinstance(cmd, Tree):
                                    self.eval(cmd, verification)

            elif name == "expression":

                identifier = self.command.children[0].value
                result = self.expression(self.command.children[1])
                self.identifiers[identifier] = result

            elif name == "operate":

                op_time = args['time']
                rising_time = args['rising_time']

                direction = helper.parse_direction(args['direction'])

                if rising_time > time:
                    self.errors.append(["warinig", name,
                                       messages.rising_time_warinig % (rising_time, op_time)])
                    rising_time = time

                #  target_rising_time = rising_time + time.time()
                target_time = op_time + time.time()

                if not verification:

                    # TODO: rising_steps = min(15, int(rising_time/2))
                    # for step in range(rising_steps):
                    #     self.pause_sleep()
                    #     self.lock.acquire()
                    #     self.lock.release()

                    self.cp_start(freq=args['frequency'], direction=direction)

                    while self.is_running and (target_time > time.time()):
                        time.sleep(0.1)
                        target_time += self.pause_sleep()

#        except Exception as err:
#            logging.info("Error eval command: " + name + " " + unicode(args) + " - " + unicode(err))
             #self.errors.append(["warinig", name,
            # todo            u"Beep duration too long: " + helper.unicode_escape(duration)])

    def program_execute_t(self, program):
        self.start_time = time.time()
        self.end_time = self.start_time + config.max_execution_time

        self.state = State.RUNNING

        self.command = None  # node of current command

        self.identifiers = {}
        self.errors = []

        self.message = ""

        self.start_time = time.time()
        self.end_time = config.max_execution_time + time.time()
        self.command_start_time = time.time()
        self.command_end_time = config.max_execution_time + time.time()

        pause(self.user_interaction, False)
        pause(self.user_pause, False)
        pause(self.pause, False)

        for node in program.children:  # start is root node
            if isinstance(node, Tree):
                self.eval(node)

        self.state = State.COMPLETED

    def program_execute(self):
        if not self.is_running and self.program:
            self.program_t = threading.Thread(name='program_execute',
                                              target=self.program_execute_t,
                                              args=(self.program,))
            self.program_t.start()

            logging.info(u"program_execute()")

    # manual
    def manual_execute_t(self, direction=None, freq=1, execution_time=1, period=0):
        self.state = State.MANUAL

        self.command_start_time = self.start_time
        if period == 0:
            self.command_end_time = self.end_time
        else:
            self.command_end_time = min(self.command_start_time + period, self.end_time)

        self.cp_start(freq, direction)

        while self.rest_time and self.is_running:

            time.sleep(self.command_rest_time)

            if self.rest_time and self.is_running:
                if period > 0:
                    self.command_start_time = self.command_end_time
                    self.command_end_time = min(self.command_start_time + period, self.end_time)

                self.lock.acquire()
                self.device.reverse()
                self.lock.release()

        self.lock.acquire()
        self.device.stop()
        self.lock.release()

        self.state = State.COMPLETED
        logging.info(u"manual complete")

    def manual_execute(self, direction=None, freq=1, execution_time=1, period=0):
        if not self.is_running:
            logging.info(u"manual_execute()")

            self.manual_t = threading.Thread(name='manual_execute',
                                             target=self.manual_execute_t,
                                             args=(direction, freq, execution_time, period))
            self.start_time = time.time()
            self.end_time = self.start_time + min(execution_time, config.max_execution_time)

            self.manual_t.start()

    def readRecipe(self, recipe=""):

        if recipe:
            self.recipeFile = recipe

        text = ""
        with open(self.recipeFile) as f:

            text = f.read()

            try:
                text = text.decode(config.codepage)
            except UnicodeDecodeError:
                pass

            if type(text) != unicode:
                try:
                    text = text.decode('utf-8')
                except UnicodeDecodeError:
                    pass

            self.program = None
            try:
                self.program = dsl.parse(text)
            except Exception as err:
                message = messages.file_error % helper.unicode_escape(err)
                helper.console(message)
                dialog.infoDialog(message, class_name="")

        if config.print_debug and self.program is not None:
            helper.console(text)
            print(self.program.pretty().encode(config.codepage))
            print(unicode(self.program).encode(config.codepage))

    # -------------------------------

    def reaction_test2(self):
        if not self.is_running:
            logging.info(u"reaction_test2(): Begin.")

            self.cp_start(2, dev.Direction.FWD)
            time.sleep(3)

            self.lock.acquire()
            self.device.stop()
            self.lock.release()
            time.sleep(1)

            self.cp_start(4, dev.Direction.REV)
            time.sleep(3)

            self.lock.acquire()
            self.device.stop()
            self.lock.release()

            logging.info(u"reaction_test2(): Complete.")
