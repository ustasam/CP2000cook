# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk  # GLib, Gio,


def selectFile(message="", parent=None, location="."):
    result = ""
    dialog = Gtk.FileChooserDialog(
        message, parent, Gtk.FileChooserAction.OPEN,
        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

    filter_recipe = Gtk.FileFilter()
    filter_recipe.set_name("Рецепт")
    filter_recipe.add_pattern("*.recipe")
    filter_recipe.add_pattern("*.Рецепт")
    dialog.add_filter(filter_recipe)

    filter_any = Gtk.FileFilter()
    filter_any.set_name("Любой тип")
    filter_any.add_pattern("*.*")
    dialog.add_filter(filter_any)

    response = dialog.run()
    if response == Gtk.ResponseType.OK:
        result =  dialog.get_filename()

    dialog.destroy()
    return result


def infoDialog(info, explains="", parent=None):
    dialog = Gtk.MessageDialog(parent, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, info)
    dialog.format_secondary_text(explains)
    dialog.run()
    dialog.destroy()


def yesNoDialog(message, parent=None, title="Вопрос."):
    dialog = Gtk.MessageDialog(
        parent, Gtk.DialogFlags.MODAL,
        Gtk.MessageType.QUESTION,
        Gtk.ButtonsType.YES_NO, message, title=title)
    response = dialog.run()
    dialog.destroy()
    if response == Gtk.ResponseType.YES:
        return True
    else:
        return False
