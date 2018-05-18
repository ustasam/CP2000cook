#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
import time

import helper
import config
import dialog
import cook
import cp2000

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk  # GLib, Gio,


class Main_GUI(object):

    def __init__(self, instrument=None, recipe=""):

        screen = Gdk.Screen.get_default()
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(config.cssfile)

        context = Gtk.StyleContext()
        context.add_provider_for_screen(
                screen, css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.gladefile = config.gladefile
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.gladefile)
        self.builder.connect_signals(self)

        self.window = self.builder.get_object("main_window")

        # controls
        self.ui_test_box = self.builder.get_object("test_box")

        self.ui_recipe = self.builder.get_object("recipe")
        self.ui_recipe_status = self.builder.get_object("recipe_status")

        self.ui_progress = self.builder.get_object("progress")
        self.ui_message = self.builder.get_object("message")
        self.ui_operation_args = self.builder.get_object("operation_args")
        self.ui_operation_state = self.builder.get_object("operation_state")
        self.ui_operation = self.builder.get_object("operation")

        self.ui_time1 = self.builder.get_object("time1")
        self.ui_time2 = self.builder.get_object("time2")
        self.ui_time3 = self.builder.get_object("time3")
        self.ui_time4 = self.builder.get_object("time4")

        self.ui_freq1 = self.builder.get_object("freq1")
        self.ui_freq2 = self.builder.get_object("freq2")
        self.ui_par = self.builder.get_object("par")
        self.ui_direction = self.builder.get_object("direction")

        self.ui_status = self.builder.get_object("status")

        # Manual control
        self.ui_manual_freq = self.builder.get_object("manual_freq")
        self.ui_manual_time = self.builder.get_object("manual_time")
        self.ui_manual_direction = self.builder.get_object("manual_direction")
        self.ui_manual_direction_time = self.builder.get_object("manual_direction_time")

        self.ui_manual_freq_label = self.builder.get_object("manual_freq_label")
        self.ui_manual_time_label = self.builder.get_object("manual_time_label")
        self.ui_manual_direction_label = self.builder.get_object("manual_direction_label")
        self.ui_manual_direction_time_label = self.builder.get_object("manual_direction_time_label")

        # notebook pages
        self.notebook = self.builder.get_object("notebook")
        self.recipe_select_page_number = 0
        self.recipe_select_page = self.notebook.get_nth_page(self.recipe_select_page_number)
        self.recipe_page_number = 1
        self.recipe_page = self.notebook.get_nth_page(self.recipe_page_number)
        self.manual_page_number = 2
        self.manual_page = self.notebook.get_nth_page(self.manual_page_number)

        self.cook = cook.Cook(instrument)

        self.load_menu()

        if recipe:
            self.cook.readRecipe(recipe)
            self.notebook.set_current_page(self.recipe_page_number)

        self.ui_update_recipe_name()
        self.ui_update_recipe()
        self.ui_update_manual()

        self.window.show()

        self.timeout_id = GObject.timeout_add(config.gui_update_period, self.on_timeout, None)

    def user_interaction_command(self):

        if self.cook.is_running and \
                cook.paused(self.cook.user_interaction) and \
                (self.cook.command is not None):

            args = self.cook.command.args if hasattr(self.cook.command, 'args') else None

            if args and self.cook.command.name == "message":
                dialog.infoDialog(args['message'], parent=self.window)

            elif args and self.cook.command.name == "parameter":
                res = dialog.textInputDialog(
                            message=args['message'],
                            value=args['default'],
                            title="Введите значение", value_message="Значение",
                            parent=self.window)

                self.cook.command.result = res
                print res

            cook.pause(self.cook.user_interaction, False)

    def on_timeout(self, arg):

        self.cook.lock.acquire()

        try:
            self.ui_notebook_update()

            # if cook.State.is_manual(self.cook.state):
            self.ui_update_manual()
            # if cook.State.is_program(self.cook.state):
            self.ui_update_recipe()

            if cook.paused(self.cook.user_interaction):
                self.user_interaction_command()

        except Exception as err:
            logging.error("error on_timeout(): " + str(err))

        self.cook.lock.release()

        milliseconds = config.gui_update_period
        if cook.State.is_stopped(self.cook.state):
            milliseconds = 2000 - (time.time() % 1) * 1000

        self.timeout_id = GObject.timeout_add(milliseconds, self.on_timeout, None)

    def ui_update_recipe(self):

        if self.cook.command is not None and self.cook.is_running:
            if self.cook.message:
                self.ui_message.set_text(self.cook.message)
            else:
                self.ui_message.set_text(self.cook.name)

            self.ui_operation.set_text(self.cook.command.loc_name)

            args = u""
            for key, value in self.cook.command.args.iteritems():
                if type(value) == unicode:  # get_command_argument_loc_name
                    args = args + key + ":" + value + u" , "  # .decode('unicode-escape')
                else:
                    args = args + key + ":" + str(value) + u" , "
            if args:
                args = args[:-3]

            self.ui_operation_args.set_text(args)

            self.ui_time1.set_text(helper.format_time(self.cook.command_time))
            self.ui_time2.set_text(helper.format_time(self.cook.command_total_time)
                                   if self.cook.command_total_time else "-")
            self.ui_time3.set_text(helper.format_time(self.cook.time))
            self.ui_time4.set_text(helper.format_time(self.cook.total_time)
                                   if self.cook.total_time else "-")

            self.ui_progress.set_fraction(self.cook.time / self.cook.total_time)

            self.ui_operation_state.set_text(cook.State.repr(self.cook.state))
            self.ui_status.set_text(cook.State.repr(self.cook.state))
        else:
            self.ui_message.set_text(self.cook.name)

            self.ui_operation.set_text("-")
            self.ui_operation_args.set_text("")

            self.ui_time1.set_text("")
            self.ui_time2.set_text("")
            self.ui_time3.set_text("")
            self.ui_time4.set_text("")

            self.ui_progress.set_fraction(0.0)

            self.ui_operation_state.set_text("")
            self.ui_status.set_text("")

        self.ui_freq1.set_text("%.1f" % (self.cook.device.cp_freq_current/100.0))
        self.ui_freq2.set_text("%.1f" % (self.cook.device.cp_freq_current/100.0))
        self.ui_par.set_text("")
        self.ui_direction.set_text(cp2000.Direction.repr(self.cook.device.direction))

    def ui_update_manual(self):
        self.ui_manual_freq_label.set_text("{0:.1f}".format(self.cook.device.cp_freq_current/100))
        self.ui_manual_time_label.set_text("{0:.1f}".format(self.cook.rest_time))
        self.ui_manual_direction_label.set_text(cp2000.Direction.repr(self.cook.device.direction))
        self.ui_manual_direction_time_label.set_text("{0:.1f}".format(self.cook.command_rest_time))

    def ui_notebook_update(self):
        if cook.State.is_program(self.cook.state):
            self.recipe_select_page.hide()
            self.manual_page.hide()
            self.recipe_page.show()
        elif cook.State.is_manual(self.cook.state):
            self.recipe_select_page.hide()
            self.recipe_page.hide()
            self.manual_page.show()
        else:
            self.recipe_select_page.show()
            self.recipe_page.show()
            self.manual_page.show()

    def openRecipeMenu(self):
        print("openRecipeMenu")
        pass

    def on_report_clicked(self, widget):
        print("on_report_clicked")
        pass

    def openFile(self):
        if cook.State.is_running(self.cook.state):
            dialog.infoDialog("Сначала остановите текущую операцию.", "Выполняется операция.", self.window)
        else:
            file = dialog.selectFile("Рецепт производства", self.window)
            if file != "":
                # self.cook.stop()
                logging.info("Selected file " + file)
                self.cook.readRecipe(file)

            self.ui_update_recipe_name()
            self.ui_update_recipe()
            self.ui_update_manual()
            self.notebook.set_current_page(self.recipe_page_number)

    def ui_update_recipe_name(self):
        self.ui_recipe.set_text(os.path.basename(self.cook.recipeFile))
        if self.cook.recipeFile == "":
            self.ui_message.set_text("Откройте рецепт.")
            self.ui_recipe_status.set_text("")
        else:
            self.ui_message.set_text(self.cook.name)
            self.ui_recipe_status.set_text(self.cook.recipeFile)

    def on_menu_open_activate(self, menuitem):
        logging.info("on_menu_open_activate()")
        self.openFile()

    def on_open_clicked(self, widget):
        logging.info("on_open_clicked()")
        self.openFile()

    def on_start_clicked(self, widget):
        logging.info("on_start_clicked()")
        if cook.State.is_running(self.cook.state):
            dialog.infoDialog("Сначала остановите текущую операцию.", "Выполняется операция.", self.window)
        elif not self.cook.program:
            dialog.infoDialog("Не выбран или не открыт рецепт.", "Откройте рецепт.", self.window)
        else:
            if dialog.yesNoDialog("Начать выполнение рецепта?", self.window):
                self.cook.program_execute()
                self.ui_notebook_update()

    def on_stop_clicked(self, widget):
            logging.info("on_stop_clicked()")
            self.cook.stop()

            self.ui_notebook_update()
            self.ui_update_recipe()
            self.ui_update_manual()

    def on_manual_enable_clicked(self, widget):

        if cook.State.is_running(self.cook.state):
            dialog.infoDialog("Сначала остановите текущую операцию.", "Выполняется операция.", self.window)
        else:
            if dialog.yesNoDialog("Выполнить ручную операцию?", self.window):
                logging.info("on_manual_enable_clicked()")

                freq = float(self.ui_manual_freq.get_text())
                execution_time = int(self.ui_manual_time.get_text())
                if self.ui_manual_direction.get_active():
                    direction = cp2000.Direction.FWD
                else:
                    direction = cp2000.Direction.REV
                period = int(self.ui_manual_direction_time.get_text())

                self.cook.manual_execute(direction, freq, execution_time, period)
                self.ui_notebook_update()

    def on_manual_disable_clicked(self, widget):
        self.ui_notebook_update()
        pass

    def quit(self):
        self.cook.stop()
        logging.info("quit()")
        Gtk.main_quit()

    def on_menu_quit_activate(self, menuitem):
        if dialog.yesNoDialog("Выйти из программы?", self.window):
            self.quit()

    def on_main_window_delete_event(self, widget, a):
        if dialog.yesNoDialog("Выйти из программы?", self.window):
            self.quit()
        else:
            return True

    def on_test1(self, widget):
        cp2000.cp2000_communication_test(self.cook.device.instrument)

    def on_test2(self, widget):
        self.cook.reaction_test2()

    def load_menu(self):
        with open(unicode(config.recipes_menu_file, 'utf-8')) as f:

            text = unicode(f.read(), 'utf-8')

            print text


def run_main(instrument, recipe):
    main_gui = Main_GUI(instrument, recipe)
    Gtk.main()
    main_gui = main_gui
