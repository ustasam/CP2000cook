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
            return "Остановлен"
        elif state == State.RUNNING:
            return "Выполняется"
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
        self.device.state = dev.CPState.STOPPED
        self.device.freq = helper.default(freq, self.device.freq)
        self.device.direction = helper.default(direction, self.device.direction)
        self.device.state = dev.CPState.RUNNING
        logging.info("start(): " + str(self.device.freq) + " " + dev.Direction.repr(self.device.direction))

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
        self.state = State.STOPPED
        self.device.stop()
        pause(self.user_interaction, False)
        pause(self.user_pause, False)
        pause(self.pause, False)
        logging.info("stop()")

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

            if (max_time >= time.time()):
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
            identifier = str(node.children[0].value)
            if identifier in self.identifiers:
                return self.identifiers[identifier]
            else:
                self.errors.append(["error", "expression", "Identifier %s not fount." % identifier])
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
            print "\n" + "-" * 10 + node.data + "-"*10
            print "self.identifiers=" + str(self.identifiers)
            print "self.command=" + str(self.command)
            print "self.command.args=" + str(self.command.args)
            print "+" * 10

        try:
            if name == "program_name":
                self.recipeName = args['name']

                if self.recipeName == "":
                    self.errors.append(["warinig", name, "Program has no name."])
                if not verification:
                    logging.info("% " + name + " " + str(args))

            elif name == "beep":
                if not verification:

                    for i in range(args['count']):

                        helper.playsound(args['frequency'], args['duration'] * 1000)
                        if i < (args['count'] - 1):
                            time.sleep(args['pause'])

                    logging.info("% " + name + " " + str(args))
                else:
                    duration = (args['duration'] * args['count'] + args['pause'] * (args['count'] - 1))
                    if duration > 15:
                        self.errors.append(["warinig", name,
                                            "Beep duration too long: " + str(duration)])

            elif name == "pause":
                if not verification:

                    pause(self.pause)
                    self.pause_sleep(max_duration=args['duration'])
                    pause(self.pause, False)

                    logging.info("% " + name + " " + str(args))

            elif name == "end":
                if not verification:
                    self.stop()
                    self.state = State.COMPLETED
                    logging.info("% " + name + " " + str(args))

            elif name == "parameter":
                if not verification:
                    pause(self.user_interaction)
                    self.user_interaction.wait()

                    self.identifiers[args['name']] = self.command.result

                    logging.info("% " + name + " " + str(args))

            elif name == "message":
                if not verification:
                    pause(self.user_interaction)
                    self.user_interaction.wait()
                    logging.info("% " + name + " " + str(args))

            elif name == "repeat":
                if not verification:
                    # for i in node.children:
                    #     if isinstance(i, Tree):
                    #         self.eval(i, verification)
                    logging.info("% " + name + " " + str(args))

            elif name == "expression":

                identifier = self.command.children[0].value
                result = self.expression(self.command.children[1])

                self.identifiers[identifier] = result

            elif name == "operate":
                op_time = helper.parse_time(args['time'])
                rising_time = helper.parse_time(args['rising_time'])

                direction = helper.parse_direction(dsl.direction(args['direction']))

                if rising_time > time:
                    self.errors.append(["warinig", name,
                                       messages.rising_time_warinig % (rising_time, op_time)])
                    rising_time = time

                target_rising_time = rising_time + time.time()
                target_time = op_time + time.time()

                if not verification:

                    # TODO: rising_steps = min(15, int(rising_time/2))
                    # for step in range(rising_steps):
                    #     self.pause_sleep()
                    #     self.lock.acquire()
                    #     self.lock.release()

                    self.lock.acquire()
                    self.cp_start(freq=args['frequency'], direction=direction)
                    self.lock.release()

                    while self.is_running and (target_time > time.time()):
                        time.sleep(0.1)
                        target_time += self.pause_sleep()

                    logging.info("% " + name + " " + str(args))

        except Exception as err:
            logging.info("Error eval command: " + name + " " + str(args) + " - " + str(err))

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

            logging.info("program_execute()")

    # manual
    def manual_execute_t(self, direction=None, freq=1, execution_time=1, period=0):
        self.state = State.MANUAL

        self.command_start_time = self.start_time
        if period == 0:
            self.command_end_time = self.end_time
        else:
            self.command_end_time = min(self.command_start_time + period, self.end_time)

        self.lock.acquire()
        self.cp_start(freq, direction)
        self.lock.release()

        while self.rest_time and self.is_running:

            time.sleep(self.command_rest_time)

            t_suspend = time.time()
            self.lock.acquire()
            t_suspend_correction = time.time() - t_suspend
            self.lock.release()

            self.end_time = self.end_time + t_suspend_correction
            self.command_end_time = self.command_end_time + t_suspend_correction

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
        logging.info("manual complete")

    def manual_execute(self, direction=None, freq=1, execution_time=1, period=0):
        if not self.is_running:
            logging.info("manual_execute()")

            self.manual_t = threading.Thread(name='manual_execute',
                                             target=self.manual_execute_t,
                                             args=(direction, freq, execution_time, period))
            self.start_time = time.time()
            self.end_time = self.start_time + min(execution_time, config.max_execution_time)

            self.manual_t.start()

    def readRecipe(self, recipe=""):

        if recipe:
            self.recipeFile = recipe

        with open(unicode(self.recipeFile, 'utf-8')) as f:

            text = unicode(f.read(), 'utf-8')
            print text
            self.program = None

            try:
                self.program = dsl.parse(text)
            except Exception as err:
                print("Error in recipe file. \n" + str(err))
                dialog.infoDialog("Ошибка в разборе файла рецепта. \n" + str(err))

        if self.program is not None and config.print_debug:
            print(self.program.pretty())
            print(self.program.children)

    # -------------------------------

    def reaction_test2(self):
        if not self.is_running:
            logging.info("reaction_test2(): Begin.")
            self.cp_start(2, dev.Direction.FWD)
            time.sleep(3)
            self.device.stop()
            time.sleep(1)
            self.cp_start(4, dev.Direction.REV)
            time.sleep(3)
            self.device.stop()
            logging.info("reaction_test2(): Complete.")
