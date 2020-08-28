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

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gio, GLib
from datetime import datetime

from .window import LensyWindow
from .screenshot import Screenshot


class Application(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='com.github.amikha1lov.Lensy',
                        # change this to flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE 
                        # if you need to start app from command line
                        # or flags=Gio.ApplicationFlags.FLAGS_NONE if you need a GUI
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.add_main_option(
            "screen",
            ord("s"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.NONE,
            "Create fullscreen screenshot",
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
            filename = 'Lensy_' + datetime.today().strftime('%Y-%m-%d-%H:%M:%S') + '.png'
            screenshot = Screenshot()
            screenshot.fullscreen(filename)

        return 0


def main(version):
    app = Application()
    return app.run(sys.argv)
