import math

import pyglet

from gui.utils import lerp
from gui.game_context import GameContext


class Scene(pyglet.event.EventDispatcher):
    """게임에서 사용할 장면의 부모 클래스. 인트로(게임 선택), 메인 화면 등이 예."""

    match_w_h: float = 0.5
    scale_factor: float = 1.0
    scale_factor_x: float = 1.0
    scale_factor_y: float = 1.0

    ref_w: int = 1280
    ref_h: int = 720

    def __init__(self, window: pyglet.window.Window, context: GameContext) -> None:
        self.window = window
        self.context = context
        self.active: bool = False

    def load(self):
        """저장된 Window 객체에서 Scene을 구성함."""
        self.active = True
        @self.window.event
        def on_resize(w: int, h: int) -> None:
            self.on_resize_window(w, h)
        pyglet.clock.schedule_interval(self.on_update_scene, 1/30)

    def unload(self):
        """저장된 Window 객체에서 이 Scene을 삭제. 다른 Scene으로 전환하기 전 호출할 것."""
        self.active = False
        pyglet.clock.unschedule(self.on_update_scene)

    def on_resize_window(self, w: int, h: int) -> None:
        """
        창 크기가 변할 때 호출됨.
        기본 동작: 기준 화면 해상도 대비 현재 해상도를 기반으로 크기 상수를 계산.
        Unity의 CanvasScaler를 참고.
        params:
            w: 현재 해상도의 가로.
            h: 현재 해상도의 세로.
            match_w_h: 가로 혹은 세로 변화율의 반영 비율. 0에 가까울수록 가로가, 1에 가까울수록 세로가 더 많이 반영됨."""
        self.scale_factor_x = w / self.ref_w
        self.scale_factor_y = h / self.ref_h
        self.scale_factor = math.exp(lerp(math.log(self.scale_factor_x), math.log(self.scale_factor_y), self.match_w_h))

    def on_update_scene(self, dt):
        self.dispatch_event("on_scene_updated", dt)


Scene.register_event_type("on_scene_updated")