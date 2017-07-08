import types

import pyrogi
from pyrogi.drawing import Color, SolidPaint
from pyrogi.ui import UIElement

class Button(UIElement):
    def __init__(self, screen, position, dimensions, text):
        super(Button, self).__init__(screen, position, dimensions)

        self.add_rectangle(dimensions, ' ', Color(0, 0, 0), Color(0, 0, 0))

        self.text = text
        self.write_text(text)

        self.base_paint = SolidPaint(Color(200, 200, 200))
        self.hover_paint = SolidPaint(Color(100, 100, 100))
        self.click_paint = SolidPaint(Color(70, 70, 70))
        self.text_base_paint = SolidPaint(Color(255, 255, 255))
        self.text_hover_paint = SolidPaint(Color(255, 255, 255))
        self.text_click_paint = SolidPaint(Color(255, 255, 255))

        self._update_paints()

    def on_clicked(self, event):
        raise NotImplementedError()
    def set_on_clicked(self, func):
        self.on_clicked = types.MethodType(func, self)

    def on_mouse_down(self, event):
        self._update_paints()
    def on_mouse_entered(self, event):
        self._update_paints()
    def on_mouse_left(self, event):
        self._update_paints()
    def on_mouse_button_up(self, event):
        super(Button, self).on_mouse_button_up(event)
        self._update_paints()

    def _update_paints(self):
        if self.mouse_down_on_element:
            self.bg_paint = self.click_paint
            self.fg_paint = self.text_click_paint
        else:
            if self.contains_position(pyrogi.get_mouse_position()):
                self.bg_paint = self.hover_paint
                self.fg_paint = self.text_hover_paint
            else:
                self.bg_paint = self.base_paint
                self.fg_paint = self.text_base_paint
