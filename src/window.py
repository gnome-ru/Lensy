# window.py
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

import math
import os
import threading
import time
from datetime import datetime

import cairo
import gi
from gi.repository import Gdk, GdkPixbuf, Gio, GLib, Gtk, Notify, Pango
from imgurpython import ImgurClient

from .screenshot import Screenshot

gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')


@Gtk.Template(resource_path='/com/github/amikha1lov/Lensy/window.ui')
class LensyWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'LensyWindow'
    appname = 'com.github.amikha1lov.Lensy'
    surface = None
    __drawing = False
    numberElements = 0
    brushSizeValue = 0
    currentWidth = 0
    currentHeight = 0
    image = None
    i = 0
    w = 0
    h = 0
    bus = None
    numberCounter = 0
    elements = []
    brushColorValue = [255.0, 0.0, 0.0, 1.0]
    __mouse_press_vector = None
    __mouse_current_vector = None
    __img_surface = None
    __fg_surface = None
    __tmp_surface = None
    linePoints = []
    fileName = ""
    arr_path_temp = []
    arr_path = []
    tmp_arr = []
    redo_tmp_arr = []
    main_box = Gtk.Template.Child()
    bottom_box = Gtk.Template.Child()
    color_button = Gtk.Template.Child()
    brushSizeProp = Gtk.Template.Child()
    drawArea = Gtk.Template.Child()
    undo_btn = Gtk.Template.Child()
    redo_btn = Gtk.Template.Child()
    clear_btn = Gtk.Template.Child()
    arrow_tool = Gtk.Template.Child()
    square_tool = Gtk.Template.Child()
    line_tool = Gtk.Template.Child()
    text_tool = Gtk.Template.Child()
    text_popover = Gtk.Template.Child()
    text_entry = Gtk.Template.Child()
    square_nofill_tool = Gtk.Template.Child()
    ellipse_tool = Gtk.Template.Child()
    numbers_tool = Gtk.Template.Child()
    free_tool = Gtk.Template.Child()
    save_to_file_btn = Gtk.Template.Child()
    clipboard_btn = Gtk.Template.Child()
    share_btn = Gtk.Template.Child()
    spinner_btn = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screenshot = Screenshot()
        Notify.init(self.appname)
        self.connect("delete-event", self.on_delete_event)
        # accel = Gtk.AccelGroup()
        # accel.connect(Gdk.keyval_from_name('s'), Gdk.ModifierType.CONTROL_MASK, 0, self.onSave)
        # accel.connect(Gdk.keyval_from_name('z'), Gdk.ModifierType.CONTROL_MASK, 0, self.onUndo)
        # self.add_accel_group(accel)
        self.undo_btn.set_sensitive(False)
        self.redo_btn.set_sensitive(False)
        self.clear_btn.set_sensitive(False)
        self.props.hexpand = True
        self.props.vexpand = True
        self.brushSizeValue = self.brushSizeProp.get_value()
        self.drawArea.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.drawArea.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
        self.drawArea.add_events(Gdk.EventMask.BUTTON_MOTION_MASK)
        self.fileName = "/tmp/lensy_temp.png"
        final_result = self.screenshot.from_selected_area(self.fileName)
        if not final_result[0]:
            self.notification = Notify.Notification.new("Lensy", ("Please re-select the area"))
            self.notification.show()
            final_result = self.screen_area(self.fileName)
        self.image = GdkPixbuf.Pixbuf.new_from_file(final_result[1])

        self.set_size_request(self.image.get_width(), self.image.get_height())

    @Gtk.Template.Callback()
    def onBrushSizeChange(self, widget):
        self.brushSizeValue = self.brushSizeProp.get_value()

    @Gtk.Template.Callback()
    def onColorSet(self, widget):
        rgba = widget.get_rgba()
        self.brushColorValue = [rgba.red, rgba.green, rgba.blue, rgba.alpha]

    @Gtk.Template.Callback()
    def onButtonPress(self, widget, event):
        self.__drawing = True
        self.__mouse_press_vector = [event.x, event.y]
        self.linePoints.append([event.x, event.y])

    @Gtk.Template.Callback()
    def onButtonRelease(self, widget, event):
        self.__drawing = False
        self.__mouse_current_vector = [event.x, event.y]
        del self.linePoints[:]
        self.drawArea.queue_draw()

        if self.numbers_tool.get_active():
            self.drawNumbers()
            self.arr_path.append(self.arr_path_temp)
            self.numberElements += 1

        elif (self.__mouse_press_vector[0] == self.__mouse_current_vector[0]
              or self.__mouse_press_vector[1] == self.__mouse_current_vector[1]):
            return
        else:
            self.arr_path.append(self.arr_path_temp)
            self.numberElements += 1
        if len(self.arr_path) == self.numberElements:
            self.redo_btn.set_sensitive(False)
            self.tmp_arr.clear()

    @Gtk.Template.Callback()
    def onDraw(self, area, cr):
        self.drawArea.set_size_request(self.__img_surface.get_width(),
                                       self.__img_surface.get_height())

        if self.__img_surface is None:
            return

        w = area.get_allocated_width()
        h = area.get_allocated_height()

        if not self.__fg_surface:
            self.__fg_surface = cairo.ImageSurface(cairo.Format.ARGB32, w, h)
        cr.set_source_surface(self.__img_surface, 0, 0)
        cr.paint()

        if self.arr_path:
            self.undo_btn.set_sensitive(True)
            self.clear_btn.set_sensitive(True)
            self.reDraw(cr)

        if self.__drawing:
            if not self.__tmp_surface:
                self.__tmp_surface = cairo.ImageSurface(cairo.Format.ARGB32, w, h)
            cr.set_source_surface(self.__tmp_surface)
            if self.square_tool.get_active() or self.square_nofill_tool.get_active():
                self.__draw_square(cr, True)
            if self.line_tool.get_active():
                self.drawLine(cr, True)
            if self.arrow_tool.get_active():
                self.drawArrow(cr, True)
            if self.ellipse_tool.get_active():
                self.drawEllipse(cr, True)

            if self.free_tool.get_active():
                self.drawFree(cr, True)

            cr.paint()
        elif self.__tmp_surface:
            cr.set_source_surface(self.__fg_surface, 0, 0)
            if self.square_tool.get_active() or self.square_nofill_tool.get_active():
                self.__draw_square(cr)
            if self.line_tool.get_active():
                self.drawLine(cr)
            if self.arrow_tool.get_active():
                self.drawArrow(cr)
            if self.ellipse_tool.get_active():
                self.drawEllipse(cr)
            if self.free_tool.get_active():
                self.drawFree(cr)

            self.__tmp_surface = None
        else:
            cr.set_source_surface(self.__fg_surface, 0, 0)

        cr.paint()

    @Gtk.Template.Callback()
    def onConfigure(self, area, event, data=None):
        w = area.get_allocated_width()
        h = area.get_allocated_height()

        if not self.__img_surface:
            self.__img_surface = cairo.ImageSurface.create_from_png(self.fileName)

        context = cairo.Context(self.__img_surface)
        context.set_source_rgba(1, 1, 1, 1.0)
        self.set_size_request(self.__img_surface.get_width(),
                              self.__img_surface.get_height())
        return True

    @Gtk.Template.Callback()
    def onMotion(self, area, event):
        if self.__drawing:
            self.__mouse_current_vector = [event.x, event.y]
            self.linePoints.append([event.x, event.y])
            self.drawArea.queue_draw()

    def drawFree(self, cr, draft=False):
        cr = cairo.Context(self.__img_surface)
        rgba = self.brushColorValue
        cr.set_source_rgba(rgba[0], rgba[1], rgba[2], rgba[3])
        cr.set_line_width(self.brushSizeValue)
        cr.set_line_cap(1)

        # cr.move_to(self.linePoints[0][0], self.linePoints[0][1])
        # for j in self.linePoints:
        #    cr.line_to(j[1][0], j[1][1])
        #   cr.stroke()

    def drawEllipse(self, cr, draft=False):
        cr.push_group()

        cr.save()
        cr.set_source_rgba(self.brushColorValue[0], self.brushColorValue[1], self.brushColorValue[2],
                           self.brushColorValue[3])
        cr.set_line_width(self.brushSizeValue)

        self.w = self.__mouse_current_vector[0] - self.__mouse_press_vector[0]
        self.h = self.__mouse_current_vector[1] - self.__mouse_press_vector[1]
        cr.translate(self.__mouse_press_vector[0] + self.w / 2., self.__mouse_press_vector[1] + self.h / 2.)

        cr.scale(self.w / 2., self.h / 2.)

        cr.new_path()
        cr.arc(0, 0, 1, 0, 2 * math.pi)
        cr.fill()

        cr.restore()
        coord_temp = []
        coord_temp.append(["Ellipse", self.brushColorValue, self.__mouse_press_vector[0], self.__mouse_press_vector[1],
                           self.__mouse_current_vector[0], self.__mouse_current_vector[1], self.brushSizeValue])
        cr.pop_group_to_source()

        self.arr_path_temp = coord_temp[-1]

    def drawLine(self, cr, draft=False):
        if not all([self.__mouse_press_vector, self.__mouse_current_vector]):
            return

        cr.push_group()
        cr.set_source_rgba(self.brushColorValue[0], self.brushColorValue[1], self.brushColorValue[2],
                           self.brushColorValue[3])
        cr.set_line_width(self.brushSizeValue)

        cr.move_to(*self.__mouse_press_vector)
        cr.line_to(*self.__mouse_current_vector)
        if draft:
            cr.stroke_preserve()
        else:
            cr.close_path()
        cr.stroke_preserve()
        coord_temp = []
        coord_temp.append(["Line", self.brushColorValue, self.__mouse_press_vector[0], self.__mouse_press_vector[1],
                           self.__mouse_current_vector[0], self.__mouse_current_vector[1], self.brushSizeValue])

        cr.pop_group_to_source()

        self.arr_path_temp = coord_temp[-1]

    def drawArrow(self, cr, draft=False):
        if not all([self.__mouse_press_vector, self.__mouse_current_vector]):
            return

        cr.push_group()
        cr.set_source_rgba(self.brushColorValue[0], self.brushColorValue[1], self.brushColorValue[2],
                           self.brushColorValue[3])
        cr.set_line_width(self.brushSizeValue)
        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.move_to(*self.__mouse_press_vector)

        cr.line_to(*self.__mouse_current_vector)

        cr.stroke()

        angle = math.atan2(self.__mouse_current_vector[1] - self.__mouse_press_vector[1],
                           self.__mouse_current_vector[0] - self.__mouse_press_vector[0]) + math.pi
        arrow_degrees = 0.5
        arrow_length = 20

        xA = None
        yA = None
        xB = None
        yB = None

        xA = self.__mouse_current_vector[0] + arrow_length * math.cos(angle - arrow_degrees)
        yA = self.__mouse_current_vector[1] + arrow_length * math.sin(angle - arrow_degrees)
        xB = self.__mouse_current_vector[0] + arrow_length * math.cos(angle + arrow_degrees)
        yB = self.__mouse_current_vector[1] + arrow_length * math.sin(angle + arrow_degrees)

        cr.move_to(self.__mouse_current_vector[0], self.__mouse_current_vector[1])
        cr.line_to(xA, yA)
        cr.move_to(self.__mouse_current_vector[0], self.__mouse_current_vector[1])
        cr.line_to(xB, yB)

        cr.stroke()
        if draft:
            cr.stroke_preserve()
        else:
            cr.close_path()
        cr.stroke_preserve()
        coord_temp = []
        coord_temp.append(["Arrow", self.brushColorValue, self.__mouse_press_vector[0], self.__mouse_press_vector[1],
                           self.__mouse_current_vector[0], self.__mouse_current_vector[1], self.brushSizeValue])
        cr.pop_group_to_source()
        self.arr_path_temp = coord_temp[-1]

    def drawNumbers(self):

        cr = cairo.Context(self.__img_surface)
        cr.push_group()
        cr.set_source_rgba(self.brushColorValue[0], self.brushColorValue[1], self.brushColorValue[2],
                           self.brushColorValue[3])
        cr.arc(self.__mouse_press_vector[0], self.__mouse_press_vector[1], 15, 0, 2 * math.pi)
        cr.fill()
        cr.set_source_rgba(255, 255, 255, 1)
        cr.select_font_face("Purisa", cairo.FONT_SLANT_NORMAL,
                            cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(12)

        self.numberCounter += 1

        cr.move_to(self.__mouse_press_vector[0] - 4, self.__mouse_press_vector[1] + 5)

        text = str(self.numberCounter)
        cr.show_text(text)

        coord_temp = []
        coord_temp.append(["Numbers", self.brushColorValue, self.__mouse_press_vector[0], self.__mouse_press_vector[1],
                           self.__mouse_press_vector[0] - 4, self.__mouse_press_vector[1] + 5, text])
        self.arr_path_temp = coord_temp[-1]
        cr.pop_group_to_source()

    def __draw_square(self, cr, draft=False):
        if not all([self.__mouse_press_vector, self.__mouse_current_vector]):
            return

        cr.push_group()
        cr.set_source_rgba(self.brushColorValue[0], self.brushColorValue[1], self.brushColorValue[2],
                           self.brushColorValue[3])
        cr.set_line_width(self.brushSizeValue)
        cr.move_to(*self.__mouse_press_vector)
        cr.line_to(self.__mouse_press_vector[0], self.__mouse_current_vector[1])
        cr.line_to(*self.__mouse_current_vector)
        cr.line_to(self.__mouse_current_vector[0], self.__mouse_press_vector[1])
        cr.line_to(*self.__mouse_press_vector)
        coord_temp = []
        if self.square_nofill_tool.get_active():
            if draft:
                cr.stroke_preserve()
            else:
                cr.close_path()
                cr.stroke_preserve()
            coord_temp.append(
                ["Square(NoFill)", self.brushColorValue, cr.get_current_point()[0], cr.get_current_point()[1],
                 self.__mouse_current_vector[0], self.__mouse_current_vector[1], self.brushSizeValue])
        else:
            if draft:
                cr.fill_preserve()
            else:
                cr.close_path()
                cr.fill_preserve()
            coord_temp.append(["Square", self.brushColorValue, cr.get_current_point()[0], cr.get_current_point()[1],
                               self.__mouse_current_vector[0], self.__mouse_current_vector[1], self.brushSizeValue])

        cr.pop_group_to_source()
        self.arr_path_temp = coord_temp[-1]

    @Gtk.Template.Callback()
    def on_clipboard_btn(self, button):
        out_surface = cairo.ImageSurface.create_from_png(self.fileName)
        cr = cairo.Context(out_surface)
        if self.arr_path:
            self.reDraw(cr)
        fileName = "/tmp/lensy_clipboard"
        img = out_surface.write_to_png(fileName)

        img = GdkPixbuf.Pixbuf.new_from_file(fileName)
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_image(img)
        clipboard.store()
        os.remove(fileName)

    @Gtk.Template.Callback()
    def onUndo(self, button):
        if self.arr_path:
            self.tmp_arr.append(self.arr_path.pop())
            if self.numberElements > 0:
                self.numberElements -= 1
            if self.tmp_arr[-1][0] == "Numbers":
                if self.numberCounter < 1:
                    pass
                else:
                    self.numberCounter -= 1
            self.drawArea.queue_draw()
            if len(self.arr_path) == 0:
                self.undo_btn.set_sensitive(False)

        self.redo_btn.set_sensitive(True)

    @Gtk.Template.Callback()
    def onRedo(self, button):
        self.numberCounter += 1
        if self.tmp_arr:
            self.arr_path.append(self.tmp_arr.pop())
            self.drawArea.queue_draw()
        if len(self.tmp_arr) == 0:
            self.redo_btn.set_sensitive(False)

    @Gtk.Template.Callback()
    def onClear(self, button):
        self.tmp_arr.clear()
        self.arr_path.clear()
        self.numberCounter = 0
        self.numberElements = 0
        self.clear_btn.set_sensitive(False)
        self.undo_btn.set_sensitive(False)
        self.redo_btn.set_sensitive(False)
        self.drawArea.queue_draw()

    @Gtk.Template.Callback()
    def on_save_to_file_btn_clicked(self, btn):
        dialog = Gtk.FileChooserDialog(_("Save image"), None, Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        final_filename = 'Lensy_' + datetime.today().strftime('%Y-%m-%d-%H:%M:%S') + '.png'
        dialog.set_current_name(final_filename)
        dialog.set_do_overwrite_confirmation(True)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()

            out_surface = cairo.ImageSurface.create_from_png(self.fileName)
            cr = cairo.Context(out_surface)
            if self.arr_path:
                self.reDraw(cr)
            img = out_surface.write_to_png(filename)
        dialog.destroy()

    def _open_popover_at(self, x, y):
        rectangle = Gdk.Rectangle()
        rectangle.x = x
        rectangle.y = y
        rectangle.height = 1
        rectangle.width = 1
        self.text_popover.set_pointing_to(rectangle)
        self.text_popover.set_relative_to(self)
        self.text_popover.popup()

    def reDraw(self, cr):
        for i in self.arr_path:
            if i[0] == "Square":
                cr.rectangle(i[2], i[3], i[4] - i[2], i[5] - i[3])
                cr.set_source_rgba(i[1][0], i[1][1], i[1][2], i[1][3])
                cr.fill()
                cr.set_line_width(i[6])
            elif i[0] == "Square(NoFill)":
                cr.rectangle(i[2], i[3], i[4] - i[2], i[5] - i[3])
                cr.set_source_rgba(i[1][0], i[1][1], i[1][2], i[1][3])
                cr.stroke()
                cr.set_line_width(i[6])
            elif i[0] == "Line":
                cr.set_source_rgba(i[1][0], i[1][1], i[1][2], i[1][3])
                cr.set_line_width(i[6])
                cr.set_line_cap(cairo.LINE_CAP_ROUND)
                cr.move_to(i[2], i[3])
                cr.line_to(i[4], i[5])
                cr.stroke()
            elif i[0] == "Arrow":
                cr.set_source_rgba(i[1][0], i[1][1], i[1][2], i[1][3])
                cr.set_line_width(i[6])
                cr.set_line_cap(cairo.LINE_CAP_ROUND)
                cr.move_to(i[2], i[3])
                cr.line_to(i[4], i[5])
                cr.stroke()
                angle = math.atan2(i[5] - i[3], i[4] - i[2]) + math.pi
                arrow_degrees = 0.5
                arrow_length = 20
                xA = None
                yA = None
                xB = None
                yB = None
                xA = i[4] + arrow_length * math.cos(angle - arrow_degrees)
                yA = i[5] + arrow_length * math.sin(angle - arrow_degrees)
                xB = i[4] + arrow_length * math.cos(angle + arrow_degrees)
                yB = i[5] + arrow_length * math.sin(angle + arrow_degrees)

                cr.move_to(i[4], i[5])
                cr.line_to(xA, yA)
                cr.move_to(i[4], i[5])
                cr.line_to(xB, yB)
                cr.stroke()
            elif i[0] == "Numbers":

                cr.set_source_rgba(i[1][0], i[1][1], i[1][2], i[1][3])
                cr.arc(i[2], i[3], 15, 0, 2 * math.pi)
                cr.fill()
                cr.set_source_rgba(255, 255, 255, 1)
                cr.select_font_face("Purisa", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                cr.set_font_size(12)
                text = i[6]
                if int(text) > 9:
                    cr.move_to(i[4] - 4, i[5])
                else:
                    cr.move_to(i[4], i[5])

                cr.show_text(text)
            elif i[0] == "Ellipse":
                cr.save()
                cr.set_source_rgba(i[1][0], i[1][1], i[1][2], i[1][3])
                cr.set_line_width(i[6])
                w = i[4] - i[2]
                h = i[5] - i[3]
                cr.translate(i[2] + w / 2., i[3] + h / 2.)
                cr.scale(w / 2., h / 2.)
                cr.arc(0, 0, 1, 0, 2 * math.pi)
                cr.fill()
                cr.restore()

    def on_delete_event(self, w, h):
        os.remove(self.fileName)

    @Gtk.Template.Callback()
    def on_share_btn_clicked(self, button):
        self.share_btn.set_visible(False)
        thread = threading.Thread(target=self.ImgurUpload)
        thread.daemon = True
        thread.start()

    def ImgurUpload(self):
        self.spinner_btn.set_visible(True)
        KEY = "bbe6f387229468f"
        share = cairo.ImageSurface.create_from_png(self.fileName)
        cr = cairo.Context(share)
        if self.arr_path:
            self.reDraw(cr)
        fileName = "/tmp/lensy_share.png"
        img = share.write_to_png(fileName)
        client = ImgurClient('bbe6f387229468f', None)
        image = client.upload_from_path(fileName)
        self.notification = Notify.Notification.new("Lensy", ("Success.The file link is copied to the clipboard"))
        self.notification.show()
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(image['link'], -1)
        clipboard.store()
        os.remove(fileName)
        self.spinner_btn.set_visible(False)
        self.share_btn.set_visible(True)
