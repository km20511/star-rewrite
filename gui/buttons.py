from dataclasses import dataclass
import time
from typing import Optional, TYPE_CHECKING, Tuple

import pyglet
from pyglet.gui import WidgetBase
from gui.anchored_widget import AnchorPreset, AnchoredWidget

from gui.color import Color
from gui.transitions import Transition

if TYPE_CHECKING:
    from gui.scenes.scene import Scene

@dataclass
class SolidButtonState:
    box_color: Color
    border_color: Color
    label_color: Color
    transition: float
    @staticmethod
    def lerp(a: "SolidButtonState", b: "SolidButtonState", t: float) -> "SolidButtonState":
        return SolidButtonState(
            Color.lerp(a.box_color, b.box_color, t),
            Color.lerp(a.border_color, b.border_color, t),
            Color.lerp(a.label_color, b.label_color, t),
            b.transition # 주의: Lerp로 얻은 State의 transition은 의미 있는 정보가 아님.
        )


class SolidButton(AnchoredWidget):
    """텍스트가 있는 단색 버튼.
    'on_press'와 'on_release' 이벤트를 호출함.
    """

    def __init__(
            self, 
            scene: "Scene",
            x: int, y: int, 
            width: int, height: int,
            border: int, 
            text: str,
            font_family: str,
            font_size: float,
            pressed: SolidButtonState, 
            depressed: SolidButtonState, 
            anchor: Tuple[float, float] | AnchorPreset = AnchorPreset.MiddleCenter,
            pivot: Tuple[float, float] | AnchorPreset = AnchorPreset.MiddleCenter,
            scale_factor: float = 1.0,
            hover: Optional[SolidButtonState] = None, 
            disenabled: Optional[SolidButtonState] = None,
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
        super().__init__(scene.window, x, y, width, height, anchor, pivot, scale_factor)
        self._scene = scene
        self._pressed_state = pressed
        self._depressed_state = depressed
        self._hover_state = hover or depressed
        self._disenabled_state = disenabled or depressed
        self._current_state = depressed

        self.base_font_size: float = font_size

        # TODO: add `draw` method or make Batch required.
        self._batch = batch or pyglet.graphics.Batch()
        self._user_group = group
        self._shape = pyglet.shapes.BorderedRectangle(
            x, y, width, height, border,
            color=self._current_state.box_color.tuple_256()[:3],
            border_color=self._current_state.border_color.tuple_256()[:3],
            batch=batch,
            group=group
        )
        self._label = pyglet.text.Label(
            text=text, font_name=font_family, font_size=font_size,
            color=depressed.label_color.tuple_256(),
            x=x + width//2, y=y + height//2,
            anchor_x="center", anchor_y="center", align='center',
            batch=batch,
            group=pyglet.graphics.Group(order=group.order+1, parent=group)
        )

        self._state_transition = Transition[SolidButtonState](
            self._depressed_state,
            self._pressed_state,
            self._pressed_state.transition
        )

        self._scene.push_handlers(on_scene_updated = self.update_transition, on_scene_window_resized=lambda w,h: self.update_layout())
        self._scene.window.push_handlers(
            self.on_mouse_press,
            self.on_mouse_release,
            self.on_mouse_motion
        )

        self._pressed = False

    def _update_position(self):
        self._shape.position = self._x, self._y

    def update_layout(self):
        super().update_layout(self._scene.scale_factor)
        self._update_position()
        self._shape.width, self._shape.height = self._width, self._height
        self._label.x, self._label.y = self._x + self._width/2, self._y + self._height/2
        self._label.font_size = self.base_font_size * self._scene.scale_factor

    def trigger_transition(self, start: SolidButtonState, end: SolidButtonState):
        self._state_transition.start_value = start
        self._state_transition.destination_value = end
        self._state_transition.start(time.time(), end.transition)

    def update_transition(self, dt: float):
        if not self._state_transition.active: return
        self._current_state = self._state_transition.update(time.time())
        self._shape.color = self._current_state.box_color.tuple_256()
        self._shape.border_color = self._current_state.border_color.tuple_256()
        self._label.color = self._current_state.label_color.tuple_256()

    @property
    def value(self):
        return self._pressed
    
    @value.setter
    def value(self, value):
        assert type(value) is bool, "This Widget's value must be True or False."
        self._pressed = value
        self.trigger_transition(self._current_state, self._pressed_state if value else self._depressed_state)

    # def update_groups(self, order):
    #     self._shape.group = pyglet.graphics.Group(order=order + 1, parent=self._user_group)

    def on_mouse_press(self, x, y, buttons, modifiers):
        if not self.enabled or not self._check_hit(x, y):
            return
        self.trigger_transition(self._current_state, self._pressed_state)
        self._pressed = True
        self.dispatch_event('on_press')

    def on_mouse_release(self, x, y, buttons, modifiers):
        if not self.enabled or not self._pressed:
            return
        self.trigger_transition(self._current_state, self._depressed_state)
        self._pressed = False
        self.dispatch_event('on_release')

    def on_mouse_motion(self, x, y, dx, dy):
        if not self.enabled or self._pressed:
            return
        self.trigger_transition(self._current_state, self._hover_state if self._check_hit(x, y) else self._depressed_state)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if not self.enabled or self._pressed:
            return
        
    def set_enabled(self, enabled: bool) -> None:
        """활성 상태 설정."""
        if not self.enabled ^ enabled: return
        self.enabled = enabled
        if not enabled:
            self.trigger_transition(self._current_state, self._disenabled_state)
        else:
            self.trigger_transition(self._current_state, self._depressed_state)


SolidButton.register_event_type("on_press")
SolidButton.register_event_type("on_release")
