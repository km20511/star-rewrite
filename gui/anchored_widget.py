from enum import Enum
from typing import Tuple

import pyglet
from pyglet.math import Vec2
from pyglet.gui import WidgetBase

class AnchorPreset(Enum):
    BottomLeft = 0
    BottomCenter = 1
    BottomRight = 2
    MiddleLeft = 3
    MiddleCenter = 4
    MiddleRight = 5
    TopLeft = 6
    TopCenter = 7
    TopRight = 8

class AnchoredWidget(WidgetBase):
    """창에 대한 상대적 좌표 계산 및 resize 비율을 반영하는 Widget.
    Anchor는 창의 좌측 하단을 (0,0), 우측 상단을 (1,1)로 하는 정규화된 좌표임.
    Pivot은 Anchor와 같은 형식으로, 이 위젯의 기준 좌표 역할을 하는 지점임.
    Unity의 UGUI에서 참고함."""
    def __init__(
            self,
            window: pyglet.window.Window,
            x: int, y: int, 
            width: int, height: int,
            anchor: Tuple[float, float] | AnchorPreset = AnchorPreset.MiddleCenter,
            pivot: Tuple[float, float] | AnchorPreset = AnchorPreset.MiddleCenter,
            scale_factor: float = 1.0
            ):

        self.window = window
        self.anchor: Tuple[float, float] = (
            self.anchor_from_preset(anchor) 
            if isinstance(anchor, AnchorPreset) else anchor
        )
        self.pivot: Tuple[float, float] = (
            self.anchor_from_preset(pivot) 
            if isinstance(pivot, AnchorPreset) else pivot
        )
        self.scale_factor = scale_factor
        self.base_pos: Vec2 = Vec2(x, y)
        self.base_width, self.base_height = width, height
        self._width, self._height = width * scale_factor, height * scale_factor
        super().__init__(*self.world_coord(x, y), width, height)

    def set_base_position(self, base_pos: Vec2):
        self.base_pos = base_pos
        self.update_layout()

    def set_base_size(self, base_width: int, base_height: int):
        self.base_width, self.base_height = base_width, base_height
        self.update_layout()

    def update_layout(self, scale_factor: float = -1.0):
        if scale_factor > 0: self.scale_factor = scale_factor
        self._width, self._height = self.base_width * scale_factor, self.base_height * scale_factor
        self._x, self._y = self.world_coord(*self.base_pos)

    def anchor_from_preset(self, preset: AnchorPreset) -> Tuple[float, float]:
        """Preset으로부터 실제 Anchor 반환."""
        value: int = preset.value
        return ((value % 3) / 2.0, (value // 3) / 2.0)

    def world_coord(self, x: float, y: float) -> Vec2:
        """Anchor와 Pivot을 기반으로 화면 기준 좌표를 계산."""
        return (Vec2(self.anchor[0] * self.window.width, self.anchor[1] * self.window.height)
                + Vec2(x, y)*self.scale_factor - Vec2(self.pivot[0]*self.width, self.pivot[1]*self.height))