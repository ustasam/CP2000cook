#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import logging

# import helper
import config
import dialog
import cook
import cp2000

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject  # GLib, Gio,


class Main_GUI(object):

    def __init__(self, instrument=None):
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
        self.ui_operationN = self.builder.get_object("operationN")
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
        self.recipe_select_page = self.notebook.get_nth_page(0)
        self.recipe_page = self.notebook.get_nth_page(1)
        self.state_page = self.notebook.get_nth_page(2)
        self.manual_page = self.notebook.get_nth_page(3)

        self.timeout_id = GObject.timeout_add(1000, self.on_timeout, None)

        self.cook = cook.Cook(instrument)

        self.ui_update_recipe_name()
        self.ui_update_all()
        self.ui_recipe.set_text("Рецепт.")

        self.window.show()

        self.timeout_lock = False

    def on_timeout(self, arg):
        if not self.timeout_lock:  # prevent double exetion
            self.timeout_lock = True

            try:
                if cook.State.is_running(self.cook.state):

                    self.cook.tick()

                    self.ui_update()
                    # if int(self.cook.state) & cook.State.MANUAL != 0:
                    self.ui_update_manual() if 1 else 2
                    # elif int(self.cook.state) & cook.State.PROGRAM != 0:
                    #    self.ui_update_recipe()

            except Exception as err:
                logging.error("error on_timeout(): " + str(err))

            self.timeout_lock = False

        next = 1000 - (time.time() % 1) * 1000
        self.timeout_id = GObject.timeout_add(next, self.on_timeout, None)

    def notebook_update_state(self):
        self.recipe_select_page.show()
        self.recipe_page.show()
        self.state_page.show()
        self.manual_page.show()

        if cook.State.is_manual(self.cook.state):
            # self.notebook.get_nth_page(0).hide()
            self.ui_test_box.hide()
        elif cook.State.is_program(self.cook.state):
            # self.notebook.get_nth_page(3).hide()
            self.ui_test_box.hide()

    def ui_update(self):
        pass

    def ui_update_manual(self):
        self.ui_manual_freq_label.set_text("{0:.1f}".format(self.cook.device.cp_freq_current/100))
        self.ui_manual_time_label.set_text("{0:.1f}".format(self.cook.recipe_rest_time))
        self.ui_manual_direction_label.set_text(cp2000.Direction.repr(self.cook.device.direction))
        self.ui_manual_direction_time_label.set_text("{0:.1f}".format(self.cook.command_rest_time))

    def ui_update_recipe(self):
        self.ui_progress.set_fraction(0.0)
        if self.cook.recipeFile == "":
            self.ui_message.set_text("Откройте рецепт.")
        else:
            if cook.State.is_running(self.cook.state):
                self.ui_message.set_text("")
            else:
                self.ui_message.set_text("Ожидание запуска")
        self.ui_operationN.set_text("")
        self.ui_operation_state.set_text(cook.State.repr(self.cook.state))
        self.ui_operation.set_text("")
        self.ui_time1.set_text("")
        self.ui_time2.set_text("")
        self.ui_time3.set_text("")
        self.ui_time4.set_text("")
        self.ui_freq1.set_text("")
        self.ui_freq2.set_text("")
        self.ui_par.set_text("")
        self.ui_direction.set_text("")
        self.ui_status.set_text("")

    def ui_update_all(self):
        self.ui_update()
        self.ui_update_recipe()
        self.ui_update_manual()

    def openRecipeMenu(self):
        pass

    def ui_update_recipe_name(self):
        self.ui_recipe.set_text(os.path.basename(self.cook.recipeFile))
        if self.cook.recipeFile == "":
            self.ui_message.set_text("Откройте рецепт.")
            self.ui_recipe_status.set_text("")
        else:
            if self.cook.recipeName != "":
                self.ui_recipe_status.set_text(self.cook.recipeName)  # unicode(, "cp1251")
            else:
                self.ui_recipe_status.set_text(os.path.basename(self.cook.recipeFile))

    def on_report_clicked(self, widget):
        pass

    def openFile(self):
        if cook.State.is_running(self.cook.state):
            dialog.infoDialog("Перед открытием рецепта необходимо завершить текущую операцию.")
        else:
            file = dialog.selectFile("Рецепт производства", self.window)
            if file != "":
                # self.cook.stop()
                logging.info("Selected file " + file)
                self.cook.recipeFile = file
                self.cook.readRecipe()

        self.ui_update_recipe_name()
        self.ui_update_all()

    def on_menu_open_activate(self, menuitem):
        logging.info("on_menu_open_activate()")
        self.openFile()

    def on_open_clicked(self, widget):
        logging.info("on_open_clicked()")
        self.openFile()

    def on_stop_clicked(self, widget):
        logging.info("on_stop_clicked()")
        self.cook.end()
        self.notebook_update_state()
        self.ui_update_all()

    def on_start_clicked(self, widget):
        logging.info("on_start_clicked()")
        if dialog.yesNoDialog("Начать выполнение рецепта?", self.window):
            self.cook.run()
            self.notebook_update_state()

    def on_menu_quit_activate(self, menuitem):
        logging.info("on_menu_quit_activate()")
        if dialog.yesNoDialog("Выйти из программы?", self.window):
            self.quit()

    def on_main_window_delete_event(self, widget, a):
        logging.info("on_main_window_delete_event()")
        if dialog.yesNoDialog("Выйти из программы?", self.window):
            self.quit()
        else:
            return True

    def quit(self):
        self.cook.end()
        logging.info("quit()")
        Gtk.main_quit()

    def on_manual_execute_clicked(self, widget):
        freq = float(self.ui_manual_freq.get_text())
        execution_time = int(self.ui_manual_time.get_text())
        if self.ui_manual_direction.get_active():
            direction = cp2000.Direction.FWD
        else:
            direction = cp2000.Direction.REV
        period = int(self.ui_manual_direction_time.get_text())
        self.cook.manual_execute(direction, freq, execution_time, period)
        self.notebook_update_state()
        self.ui_update_manual()

    def on_device_test1_clicked(self, widget):
        cp2000.cp2000_communication_test(self.cook.device.instrument)

    def on_device_test2_clicked(self, widget):
        self.cook.reaction_test2()
