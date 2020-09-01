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

from subprocess import PIPE, Popen

from gi.repository import Gdk, Gio, GLib, Notify


class Screenshot:

    def __init__(self):
        self.bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)

    def from_selected_area(self, filename):
        coordinate = Popen("slop -n -c 0.3,0.4,0.6,0.4 -l -t 0 -f '%w %h %x %y'",
                           shell=True, stdout=PIPE).communicate()
        listCoor = [int(i) for i in coordinate[0].decode().split()]
        if not listCoor[0] or not listCoor[1]:
            self.notification = Notify.Notification.new("Lensy", ("Please re-select the area"))
            self.notification.show()
            coordinate = Popen("slop -n -c 0.3,0.4,0.6,0.4 -l -t 0 -f '%w %h %x %y'",
                               shell=True, stdout=PIPE).communicate()
            listCoor = [int(i) for i in coordinate[0].decode().split()]
        x, y, w, h = listCoor[2], listCoor[3], listCoor[0], listCoor[1]
        temp_params = [x, y, w, h, True, filename]
        params = GLib.Variant('(iiiibs)', temp_params)
        res = self.bus.call_sync('org.gnome.Shell.Screenshot',
                                 '/org/gnome/Shell/Screenshot',
                                 'org.gnome.Shell.Screenshot',
                                 'ScreenshotArea',
                                 params,
                                 None,
                                 Gio.DBusCallFlags.NONE,
                                 -1,
                                 None)
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
