from dataclasses import dataclass
from typing import Optional

import pyglet
from pyglet.gui import WidgetBase

from gui.color import Color

class SolidButtonState:
    box_color: Color
    border_color: Color
    label_color: Color
    transition: float


class SolidButton(WidgetBase):
    """텍스트가 있는 단색 버튼.
    'on_press'와 'on_release' 이벤트를 호출함.
    """

    def __init__(
            self, 
            x: int, y: int, 
            width: int, height: int, 
            pressed: SolidButtonState, 
            depressed: SolidButtonState, 
            hover: Optional[SolidButtonState] = None, 
            batch: Optional[pyglet.graphics.Batch] = None, 
            group: Optional[pyglet.graphics.Group] = None
        ):
        """단색 버튼 생성.
        TODO: PushButton에서 베낀 코드임. 다 고치면 지울 것.

        params:
            x: 버튼 x 좌표.
            y: 버튼 y 좌표.
            pressed: 버튼이 눌렸을 때의 상태.
            depressed: 버튼이 눌리지 않았을 때의 상태.
            hover: 커서를 올렸을 때의 상태.
            batch: 이 버튼의 Batch 객체.
            group: 이 버튼이 속하는 Group.
        """
        super().__init__(x, y, width, height)
        self._pressed_img = pressed
        self._depressed_img = depressed
        self._hover_img = hover or depressed

        # TODO: add `draw` method or make Batch required.
        self._batch = batch or pyglet.graphics.Batch()
        self._user_group = group
        bg_group = pyglet.graphics.Group(order=0, parent=group)
        self._sprite = pyglet.sprite.Sprite(self._depressed_img, x, y, batch=batch, group=bg_group)

        self._pressed = False

    def _update_position(self):
        self._sprite.position = self._x, self._y, 0

    @property
    def value(self):
        return self._pressed
    
    @value.setter
    def value(self, value):
        assert type(value) is bool, "This Widget's value must be True or False."
        self._pressed = value
        self._sprite.image = self._pressed_img if self._pressed else self._depressed_img

    def update_groups(self, order):
        self._sprite.group = pyglet.graphics.Group(order=order + 1, parent=self._user_group)

    def on_mouse_press(self, x, y, buttons, modifiers):
        if not self.enabled or not self._check_hit(x, y):
            return
        self._sprite.image = self._pressed_img
        self._pressed = True
        self.dispatch_event('on_press')

    def on_mouse_release(self, x, y, buttons, modifiers):
        if not self.enabled or not self._pressed:
            return
        self._sprite.image = self._hover_img if self._check_hit(x, y) else self._depressed_img
        self._pressed = False
        self.dispatch_event('on_release')

    def on_mouse_motion(self, x, y, dx, dy):
        if not self.enabled or self._pressed:
            return
        self._sprite.image = self._hover_img if self._check_hit(x, y) else self._depressed_img

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if not self.enabled or self._pressed:
            return