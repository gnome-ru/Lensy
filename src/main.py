# main.py
#
# Copyright 2020 Alexey Mikhailov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import gi
import time

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gio, GLib
from datetime import datetime

from .window import LensyWindow
from .screenshot import Screenshot


class Application(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='com.github.amikha1lov.Lensy',
                         flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)
        self.add_main_option(
            "screen",
            ord("s"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.NONE,
            "Create fullscreen screenshot",
            None,
        )
        self.add_main_option(
            "d",
            ord("d"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.INT,
            "Delay screenshot",
            None,
        )

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = LensyWindow(application=self)
        print('activate')
        win.present()

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        options = options.end().unpack()

        if "screen" in options:
            if "d" in options:
                delay = options['d']
                time.sleep(delay)
            filename = 'Lensy_' + datetime.today().strftime('%Y-%m-%d-%H:%M:%S') + '.png'
            screenshot = Screenshot()
            screenshot.fullscreen(filename)
        else:
            self.activate()

        return 0


def main(version):
    app = Application()
    return app.run(sys.argv)
