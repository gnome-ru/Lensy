# screenshot.py
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

from gi.repository import Gdk, Gio, GLib

class Screenshot:

    def __init__(self):
        self.bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)

    def from_selected_area(self, filename):
        coords = self.bus.call_sync('org.gnome.Shell.Screenshot',
                                        '/org/gnome/Shell/Screenshot',
                                        'org.gnome.Shell.Screenshot',
                                        'SelectArea',
                                        None,
                                        GLib.VariantType.new('(iiii)'),
                                        Gio.DBusCallFlags.NONE,
                                        -1,
                                        Gio.Cancellable.get_current())
        x,y,w,h = coords.unpack()
        temp_params = [x,y,w,h, True, filename]
        params = GLib.Variant('(iiiibs)', temp_params)
        res = self.bus.call_sync('org.gnome.Shell.Screenshot',
                                        '/org/gnome/Shell/Screenshot',
                                        'org.gnome.Shell.Screenshot',
                                        'ScreenshotArea',
                                        params,
                                        None,
                                        Gio.DBusCallFlags.NONE,
                                        -1,
                                        Gio.Cancellable.get_current())
        final_result = res.unpack()
        return final_result


    def fullscreen(self, filename):
        temp_params = [True, True, filename]
        params = GLib.Variant('(bbs)', temp_params)
        self.bus.call_sync('org.gnome.Shell.Screenshot',
                        '/org/gnome/Shell/Screenshot',
                        'org.gnome.Shell.Screenshot',
                        'Screenshot',
                        params,
                        None,
                        Gio.DBusCallFlags.NONE,
                        -1,
                        None)
