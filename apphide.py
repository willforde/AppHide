#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 William Forde
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# Standard library imports
from collections import defaultdict
from functools import lru_cache
import logging
import hashlib
import shutil
import json
import sys
import os

# XDG Package imports
import xdg.Exceptions
import xdg.DesktopEntry
import xdg.BaseDirectory

# Import Gtk 3.0 Specifically
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import Pango

__repo__ = "https://github.com/willforde/AppHide.git"
__copyright__ = "Copyright (C) 2016 William Forde"
__author__ = "William Forde"
__license__ = "GPLv2"
__version__ = "0.2.0"

# Constants
DESKTOP = os.environ.get("XDG_CURRENT_DESKTOP")
DEFAULT_ICON = "application-default-icon"

# Logging
logger = logging.getLogger("apphide")
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setLevel(logging.DEBUG)
logger.addHandler(consoleHandler)


class AppHideApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.apphide.py", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.window = None

    def do_activate(self):
        if not self.window:
            self.window = AppHideWin(application=self, title="AppHide")
            self.window.connect("delete-event", self.on_quit)
            self.window.show_all()
        self.window.present()

    def on_quit(self, *_):
        if self.window.row_changed:
            self.info_dialog()
        self.quit()

    def info_dialog(self):
        """Display a error dialog when unable to hide/unhide an application"""
        dialog = Gtk.MessageDialog(self.window, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "Action Required")
        dialog.format_secondary_text("You may need to logout and login again for change to take effect")
        dialog.run()
        dialog.destroy()


class AppHideWin(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_icon_name(DEFAULT_ICON)
        self.set_default_size(860, 800)
        self.filter_by = None

        # Scrolledwindow to scroll through all applications
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(False)
        scrolledwindow.set_vexpand(True)
        scrolledwindow.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.add(scrolledwindow)

        # Outer box to store the filter box and listbox
        outer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        outer_box.set_halign(Gtk.Align.CENTER)
        outer_box.set_valign(Gtk.Align.START)
        outer_box.set_size_request(860, -1)
        outer_box.set_margin_right(16)
        outer_box.set_margin_left(16)
        scrolledwindow.add(outer_box)

        # Listbox to list all applications
        self.listbox = Gtk.ListBox()
        self.listbox.connect("row-activated", self.on_row_activated)
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        outer_box.pack_end(self.listbox, True, True, 0)

        # Fetch list of all applications and sort by name
        try:
            xdg_apps = get_xdg_apps()
        except OSError as e:
            self.error_dialog("Failed to read aplication data. Sorry", e)
            logger.error(e)
            kwargs["application"].quit()
        else:
            # Add all found applications to the listbox
            for xdg_app in xdg_apps:
                row = ListBoxRowApp()
                row.btn_hide.connect("clicked", self.on_hide_clicked, row, xdg_app)
                row.set_icon(xdg_app.icon)
                row.set_name(xdg_app.name)
                row.set_description(xdg_app.description)
                row.hidden = xdg_app.nodisplay
                self.listbox.add(row)

        # Install filter to filter resutls to all / Hidden / UnHidden
        self.listbox.set_filter_func(self.filter_listbox, None, False)
        self.listbox.set_header_func(self.header_func, None)
        self.listbox.show_all()

        # Filter box to store the filter radio button
        filter_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        filter_box.set_halign(Gtk.Align.CENTER)
        filter_box.set_valign(Gtk.Align.START)
        outer_box.pack_start(filter_box, True, True, 0)

        # All Radio Button
        btn_filter_all = Gtk.RadioButton.new_with_label_from_widget(None, "All")
        btn_filter_all.connect("toggled", self.on_radio_toggled, None)
        btn_filter_all.set_tooltip_text("Show all applications")
        filter_box.pack_start(btn_filter_all, False, False, 0)

        # Hidden Radio Button
        btn_filter_hidden = Gtk.RadioButton.new_with_label_from_widget(btn_filter_all, "Hidden")
        btn_filter_hidden.connect("toggled", self.on_radio_toggled, "Hidden")
        btn_filter_hidden.set_tooltip_text("Show only hidden applications")
        filter_box.pack_start(btn_filter_hidden, False, False, 0)

        # UnHidden Radio Button
        btn_filter_unhidden = Gtk.RadioButton.new_with_label_from_widget(btn_filter_all, "Not Hidden")
        btn_filter_unhidden.connect("toggled", self.on_radio_toggled, "UnHidden")
        btn_filter_unhidden.set_tooltip_text("Show only unhidden applications")
        filter_box.pack_start(btn_filter_unhidden, False, False, 0)
        self.row_changed = False

    @staticmethod
    def header_func(row, before, _):
        existing_header = row.get_header()
        if existing_header:
            if before:
                existing_header.show()
            else:
                existing_header.hide()
        elif before:
            separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            row.set_header(separator)

    def on_radio_toggled(self, _, filter_by):
        if not self.filter_by == filter_by:
            self.filter_by = filter_by
            self.listbox.invalidate_filter()
            self.listbox.invalidate_headers()

    def filter_listbox(self, row, *_):
        if self.filter_by is None:
            return True
        elif self.filter_by == "Hidden":
            return row.hidden
        else:
            return not row.hidden

    def error_dialog(self, error_msg, error_obj):
        """Display a error dialog when unable to hide/unhide an application"""
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.CANCEL, error_msg)
        dialog.format_secondary_text(str(error_obj))
        dialog.run()
        dialog.destroy()

    def on_hide_clicked(self, button, row, xdg_file):
        # Set label of button to Hide/UnHide, depending on active state
        active = button.get_active()
        try:
            xdg_file.nodisplay = active
        except OSError as e:
            button.set_active(not active)
            self.error_dialog("Failed to %s %s" % ("Hide" if active else "Show", xdg_file.name), e)
        else:
            text = "Show" if active else "Hide"
            button.set_label(text)
            button.set_tooltip_text("%s application" % text)
            self.row_changed = True
            row.changed()

    @staticmethod
    def on_row_activated(_, row):
        row.hidden = not row.hidden


class ListBoxRowApp(Gtk.ListBoxRow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        iner_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        iner_box.set_margin_top(16)
        iner_box.set_margin_bottom(16)
        self.add(iner_box)

        # Icon
        self._app_icon = Gtk.Image()
        self._app_icon.set_pixel_size(64)
        self._app_icon.set_valign(Gtk.Align.CENTER)
        self._app_icon.set_halign(Gtk.Align.START)
        iner_box.pack_start(self._app_icon, True, True, 16)

        # Name
        self._app_name = WrapedLabel()
        self._app_name.set_size_request(165, -1)
        self._app_name.set_max_width_chars(20)
        iner_box.pack_start(self._app_name, True, True, 0)

        # Description
        self._app_description = WrapedLabel()
        self._app_description.set_size_request(400, -1)
        self._app_description.set_max_width_chars(50)
        self._app_description.set_margin_left(16)
        iner_box.pack_start(self._app_description, True, True, 16)

        # Button
        self.btn_hide = Gtk.ToggleButton("Hide")
        self.btn_hide.set_size_request(100, -1)
        self.btn_hide.set_halign(Gtk.Align.END)
        self.btn_hide.set_valign(Gtk.Align.CENTER)
        self.btn_hide.set_tooltip_text("Hide application")
        iner_box.pack_start(self.btn_hide, True, True, 24)

    def set_name(self, name):
        """Set the name of application"""
        self._app_name.set_label(name)

    def set_icon(self, icon):
        """Set the Icon of the application"""
        self._app_icon.set_from_icon_name(icon, Gtk.IconSize.DIALOG)

    def set_description(self, description):
        """Set the description of the application"""
        self._app_description.set_label(description)

    @property
    def hidden(self):
        """Return True/False if the row is hidden or not"""
        return self.btn_hide.get_active()

    @hidden.setter
    def hidden(self, value):
        """Set the state of the toggle button"""
        self.btn_hide.set_active(value)


class WrapedLabel(Gtk.Label):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set line count to 3 and enable line wrap
        self.set_lines(3)
        self.set_line_wrap(True)

        # Set line wrap to work-char and ensure that it cuts out at the end of the third line
        self.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.set_ellipsize(Pango.EllipsizeMode.END)

        # Align text to left side of widget
        self.set_xalign(0.0)

        # Align text box to top and to the left
        self.set_valign(Gtk.Align.START)
        self.set_halign(Gtk.Align.START)


class Tracker(object):
    """
    Keep track of a SHA256 hash of all xdg files that have been moved into user's xdg directory.
    This allowed the program to detect if a xdg file was modified by the user outside of this program.
    Perventing this program from removing or replacing user modified xdg files.
    Instead xdg file will be modified inplace.
    """
    _config_dir = xdg.BaseDirectory.save_config_path("apphide")
    _tracked_file = os.path.join(_config_dir, "tracker.json")
    _tracked_old_dir = os.path.join(_config_dir, "tracker")

    def __init__(self):
        self._hashes = {}
        self._changed = False

        # Load tracked data if config directory exists
        if os.path.exists(self._config_dir):
            # Load in tracked file hashes
            if os.path.exists(self._tracked_file):
                with open(self._tracked_file, "r") as stream:
                    self._hashes = json.load(stream)
                    self.cleanup()

            # Load & migrate tracked files from older version
            elif os.path.exists(self._tracked_old_dir):
                self.migrate()
        else:
            # Create missing config directory
            os.makedirs(self._config_dir)

    def __contains__(self, filepath):
        """Return True/False if given file exists within tracker"""
        return filepath in self._hashes

    def add(self, filepath):
        """Add the hash of the given file to be tracked"""
        self._hashes[filepath] = self.hash_file(filepath)
        self._changed = True

    def remove(self, filepath):
        """Remove given file's hash from the tracker"""
        del self._hashes[filepath]
        self._changed = True

    def compare(self, filepath):
        """Compare hash of given file with the stored hash"""
        file_hash = self.hash_file(filepath)
        if self._hashes[filepath] == file_hash:
            return True
        else:
            logger.debug("Store hash is not a match for file: %s", filepath)
            logger.debug("%s != %s", self._hashes[filepath], file_hash)
            self.remove(filepath)
            return False

    def save(self):
        if self._changed:
            self._changed = False
            with open(self._tracked_file, "w") as stream:
                json.dump(self._hashes, stream)

    def migrate(self):
        """Migrate from the older style of tracking to the new style"""
        for xdg_file in os.listdir(self._tracked_old_dir):
            if xdg_file.endswith(".desktop"):
                xdg_path = os.path.join(xdg.BaseDirectory.save_data_path("applications"), xdg_file)
                if os.path.exists(xdg_path):
                    self.add(xdg_path)

        # Remove all old tracked data & save
        shutil.rmtree(self._tracked_old_dir)
        self.save()

    def cleanup(self):
        """Keep the tracker clean of files that don't exist anymore"""
        for filepath in self._hashes.keys():
            if not os.path.exists(filepath):
                self.remove(filepath)

    @staticmethod
    def hash_file(filepath):
        """Return a sha256 hash of a givin file"""
        hasher = hashlib.sha224()

        # Read in file and update the hasher
        with open(filepath, "rb") as stream:
            hasher.update(stream.read())

        # Return a sha224 hash of the file
        return hasher.hexdigest()


def get_xdg_apps():
    """
    Scan the Application directory for valid desktop entries.
    Returns a list of all xdg apps found. 
    """
    xdg_files = defaultdict(list)
    for data_dir in xdg.BaseDirectory.xdg_data_dirs:
        # Skip if applications directory does not exist
        app_dir = os.path.join(data_dir, "applications")
        if not os.path.exists(app_dir):
            continue

        # Find all .desktop files within applications folder
        for app_name in os.listdir(app_dir):
            if app_name.endswith(".desktop"):
                app_path = os.path.join(app_dir, app_name)
                xdg_files[app_name].append(app_path)

    # Load all found .desktop files
    filtered_apps = []
    for app in xdg_files.values():
        xdg_data = XDGManager(app)
        if xdg_data:
            filtered_apps.append(xdg_data)
    return sorted(filtered_apps, key=lambda data: data.name.lower())


class XDGManager(object):
    """Manager to handle loading and changing of xdg files."""
    _tracker = None

    def __init__(self, app):
        self.xdg_files = app
        self.user_files = []
        self.system_files = []

        # Slip files into system/user lists
        for xdg_file in app:
            if xdg_file.startswith(xdg.BaseDirectory.xdg_data_home):
                self.user_files.append(xdg_file)
            else:
                self.system_files.append(xdg_file)

        # Load the top level xdg file
        self.xdg_data = self.parse(self.xdg_files[0])
        self.filename = os.path.basename(self.xdg_files[0])
        self.cleanup()

    @property
    def tracker(self):
        """File tracker"""
        if XDGManager._tracker is None:
            XDGManager._tracker = Tracker()
        return XDGManager._tracker

    def cleanup(self):
        """Cleanup any leftover xdg file if app has been uninstalled."""
        if self.user_files and not self.system_files and self.user_files[0] in self.tracker:
            logger.debug("Detected uninstalled app: %s, removing leftover file: %s", self.name, self.user_files[0])
            self.tracker.remove(self.user_files[0])
            self.xdg_data = None

            try:
                os.remove(self.user_files[0])
            except OSError:
                logger.debug("Failed to remove leftover file.")

            self.tracker.save()

    def __bool__(self):
        """Return True if this is an Application and that it's allowed to be show on current desktop"""
        if self.xdg_data and self.xdg_data.getType() == "Application":
            # Hide app if we have not user file and if nodisplay is set to True by default
            if not self.user_files and self.nodisplay:
                return False

            # Check that current desktop is not one of the restricted desktops
            elif DESKTOP in self.xdg_data.getNotShowIn():
                return False

            # Check if this app is allowd to be shown on current desktop
            elif self.xdg_data.getOnlyShowIn() and DESKTOP not in self.xdg_data.getOnlyShowIn():
                return False

            # Default to allow application
            else:
                return True
        else:
            return False

    @property
    def name(self):
        """Name of application"""
        return self.xdg_data.getName()

    @property
    def icon(self):
        """Icon image associated with application"""
        return self.xdg_data.getIcon()

    @property
    def description(self):
        """Description of application"""
        return self.xdg_data.getComment()

    @property
    def nodisplay(self):
        """State of the nodisplay option"""
        return self.xdg_data.getNoDisplay()

    @nodisplay.setter
    def nodisplay(self, state):
        """Hide or show an application by changing the state of NoDisplay."""
        # Ignore change if nodisplay is already the required state
        # Can happen when called via command line
        if self.nodisplay == state:
            return

        log_state = "Hiding application: %s" if state else "Showing application: %s"
        logger.info(log_state, self.name)
        src_xdg_data = self.source_data()
        dst = self.save_path()

        # If src_xdg_data is not the same as xdg_data then we must have loaded it from system
        from_source = not src_xdg_data.filename is dst

        # Remove user xdg file and revert back to source xdg file if source file has required state
        # and it was loaded from system. Keeps the system clean of unnecessary files.
        if from_source and src_xdg_data.getNoDisplay() == state:
            logger.debug("Switching to using source xdg file. Removing user xdg file: %s", dst)
            self.tracker.remove(dst)
            os.remove(dst)
        else:
            src_xdg_data.set("NoDisplay", str(state).lower(), "Desktop Entry")
            src_xdg_data.write(dst)

            # Track the new xdg file, so that the file can be checked if it was modified
            # We don't want to override the user file from source, if the user modified it
            if from_source:
                self.tracker.add(dst)

        self.tracker.save()
        self.xdg_data = src_xdg_data

    def source_data(self):
        """Return path to the source ".desktop" file, of this application."""
        if len(self.xdg_files) == 1:
            return self.xdg_data

        if not self.system_files or not self.user_files:
            return self.xdg_data
        else:
            save_path = self.save_path()
            if os.path.exists(save_path) and save_path in self.tracker and self.tracker.compare(save_path):
                return self.parse(self.system_files[0])
            else:
                return self.xdg_data

    @lru_cache(maxsize=None)
    def save_path(self):
        """Return path to the user's ".desktop" file, of this applicaion."""
        if self.xdg_files[0].startswith(xdg.BaseDirectory.xdg_data_home):
            return self.xdg_files[0]
        else:
            if "flatpak/exports" in self.xdg_files[0]:
                for path in xdg.BaseDirectory.xdg_data_dirs:
                    if path.startswith(xdg.BaseDirectory.xdg_data_home) and "flatpak/exports" in path:
                        return os.path.join(path, "applications", self.filename)

        # Default to user's xdg save_data_path
        app_dir = xdg.BaseDirectory.save_data_path("applications")
        return os.path.join(app_dir, self.filename)

    @staticmethod
    def parse(filepath):
        """Parse the given xdg file"""
        try:
            return xdg.DesktopEntry.DesktopEntry(filepath)
        except xdg.Exceptions.ParsingError as e:
            logger.error("Failed to Parse XDG file: %s", e.file)
            logger.error(e.msg)
            raise

    def __repr__(self):
        return "XDGManager({})".format(repr(self.xdg_files))

_app = AppHideApp()
exit_status = _app.run(sys.argv)
sys.exit(exit_status)
