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

    dialog.set_icon_name("applications-graphics")
    # dialog.get_style_context().add_class("dialog")

    response = dialog.run()
    if response == Gtk.ResponseType.OK:
        result =  dialog.get_filename()

    dialog.destroy()
    return result


def infoDialog(info, explains="", parent=None, class_name="dialog"):
    dialog = Gtk.MessageDialog(parent, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, info)
    dialog.set_icon_name("applications-graphics")
    if class_name:
        dialog.get_style_context().add_class(class_name)
    dialog.format_secondary_text(explains)
    dialog.run()
    dialog.destroy()


def yesNoDialog(message, parent=None, title="Вопрос."):
    dialog = Gtk.MessageDialog(
        parent, Gtk.DialogFlags.MODAL,
        Gtk.MessageType.QUESTION,
        Gtk.ButtonsType.YES_NO, message, title=title)

    dialog.set_icon_name("applications-graphics")
    dialog.get_style_context().add_class("dialog")

    response = dialog.run()
    dialog.destroy()
    if response == Gtk.ResponseType.YES:
        return True
    else:
        return False


# def responseToDialog(entry, dialog, response):
#     print response
#     dialog.response(response)

# TODO: formatter

def textInputDialog(message, value="", title="", format="", value_message="Значение", parent=None):

    dialog = Gtk.MessageDialog(parent,
                               Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                               Gtk.MessageType.QUESTION,
                               Gtk.ButtonsType.OK,
                               None, message, title=title)

    dialog.set_markup(message)

    hbox = Gtk.HBox()
    hbox.pack_start(Gtk.Label(value_message + ":"), False, 5, 5)

    entry = Gtk.Entry()
    entry.set_text(value)
    # entry.connect("activate", responseToDialog, dialog, Gtk.ButtonsType.OK)

    hbox.pack_end(entry, False, 5, 5)

    # dialog.format_secondary_markup("")  # identification
    dialog.vbox.pack_end(hbox, True, True, 0)

    dialog.set_icon_name("applications-graphics")
    dialog.get_style_context().add_class("dialog")

    dialog.show_all()
    dialog.run()

    text = entry.get_text()

    dialog.destroy()

    return text
