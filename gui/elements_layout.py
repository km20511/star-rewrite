import time

import pyglet
from pyglet.math import Vec2
from pyglet.event import EventDispatcher

from gui.scenes import Scene
from gui.transitions import Transition
from gui.utils import clamp, lerp

class ElementsLayoutBase(EventDispatcher):
    """카드, 아이템 등의 위치를 관리하는 객체의 기본 클래스."""
    def __init__(self, scene: Scene, length: int) -> None:
        self.scene: Scene = scene
        self.length: int = length

    def get_position(self, index: int) -> Vec2:
        """index번째 요소의 위치를 반환."""
        return Vec2(0, 0)

    def get_rotation(self, index: int) -> float:
        """index번째 요소의 회전을 반환."""
        return 0.0
    
    def get_scale(self, index: int) -> float:
        """index번째 요소의 크기 계수를 반환."""
        return 1.0
    
ElementsLayoutBase.register_event_type("on_layout_modified")
    

class CardsLayout(ElementsLayoutBase):
    """카드 목록을 관리하는 레이아웃 객체.
    카드 중앙을 기준으로 좌표를 계산함."""
    def __init__(
            self, 
            scene: Scene, 
            length: int,
            space: int = 300,
            y: int = 0,
            height: int = 400,
            center_scale: float = 1.3,
            scale_width: float = 0.6,
            initial_scroll: float = 0.0,
            selected: int = 0,
            scroll_sensitivity: float = 1.0
            ) -> None:
        """CardsLayout의 초기화 함수.
        params:
            `scene`: Scene - 이 객체가 존재하는 Scene.
            `length`: int - 보유한 카드 수.
            `space`: int - 카드의 기준점에서 인접 카드의 기준점까지의 거리.
            `y`: int - 창 중앙에서부터의 y좌표.
            `height`: int - 레이아웃의 세로 길이. 스크롤 시 커서 위치 검사에 사용.
            `center_scale`: float - 중앙 카드의 크기 보정치.
            `scale_width`: float - 크기를 보정할 카드가 위치하는 창의 범위.
            `initial_scroll`: float - 초기 스크롤 값. 0인 경우 가장 왼쪽 카드가 화면 중앙에 위치.
            `selected`: int - 현재 선택된 카드 인덱스.
            `scroll_sensitivity`: float - 스크롤 속력."""
        super().__init__(scene, length)
        self.space: int = space
        self.y: int = y
        self.height: int = height
        self.center_scale: float = center_scale
        self.scale_width: float = scale_width
        self.scroll_value: float = initial_scroll
        self.input_scroll: float = 0.0
        self.scroll_sensitivity: float = scroll_sensitivity
        self.selected: int = selected
        self.scroll_transition: Transition = Transition(self.scroll_value, float(selected * space), 1.0)
        self.scroll_transition.start(time.time())

        @self.scene.event
        def on_scene_updated(dt: float):
            if self.scroll_transition.active:
                self.scroll_value = self.scroll_transition.update(time.time())
                self.dispatch_event("on_layout_modified")

        @self.scene.window.event
        def on_mouse_scroll(x: int, y: int, scroll_x: float, scroll_y: float):
            if abs(y - (self.scene.window.height//2 + self.y*self.scene.scale_factor)) > self.height*self.scene.scale_factor // 2:
                return
            scroll_delta: float = (scroll_x + scroll_y) * self.scroll_sensitivity * self.scene.scale_factor
            if scroll_delta * self.input_scroll < 0:
                self.input_scroll = scroll_delta
            else:
                self.input_scroll += scroll_delta
            prev_selected: int = self.selected
            if self.input_scroll > self.space and self.selected < self.length - 1:
                self.selected += 1
            elif self.input_scroll < -self.space and self.selected > 0:
                self.selected -= 1
            if self.selected != prev_selected:
                self.input_scroll = 0.0
                self.scroll_transition.start_value = self.scroll_value
                self.scroll_transition.destination_value = float(self.space * self.selected)
                self.scroll_transition.start(time.time())
                self.dispatch_event("on_selection_changed", self.selected)

        @self.scene.window.event
        def on_key_press(symbol, modifier):
            prev_selected: int = self.selected
            if symbol == pyglet.window.key.RIGHT and self.selected < self.length - 1:
                self.selected += 1
            elif symbol == pyglet.window.key.LEFT and self.selected > 0:
                self.selected -= 1
            if self.selected != prev_selected:
                self.input_scroll = 0.0
                self.scroll_transition.start_value = self.scroll_value
                self.scroll_transition.destination_value = float(self.space * self.selected)
                self.scroll_transition.start(time.time())
                self.dispatch_event("on_selection_changed", self.selected)

        # @self.scene.window.event
        # def on_resize(w: int, h: int):
        #     self.dispatch_event("on_layout_modified")
        self.scene.push_handlers(on_scene_window_resized=lambda w,h: self.dispatch_event("on_layout_modified"))

    # def _nearest_index(start: float, space: float, length: int, target: float) -> int:
    #     """target과 가장 가까운 등차수열 항의 번호를 계산."""
    #     index: int = round((target - start) / space)
    #     return 0 if index < 0 else (length - 1 if index >= length else index)

    def get_position(self, index: int) -> Vec2:
        return Vec2(self.space*index - self.scroll_value, self.y) * self.scene.scale_factor + Vec2(self.scene.window.width // 2, self.scene.window.height // 2)
    
    def get_rotation(self, index: int) -> float:
        return 0.0
    
    def get_scale(self, index: int) -> float:
        pos_x: float = self.get_position(index).x
        normal_x: float = pos_x / self.scene.window.width
        if abs(normal_x - 0.5)*2 > self.scale_width:
            return self.scene.scale_factor
        return lerp(self.center_scale, 1.0, abs(normal_x - 0.5)*2/self.scale_width) * self.scene.scale_factor

    def get_width(self) -> int:
        """가장 왼쪽 카드의 기준점부터 가장 오른쪽 카드 기준점까지의 거리 계산.
        화면비에 영향을 받지 않는 값."""
        return self.space * (self.length-1)

CardsLayout.register_event_type("on_selection_changed")
    

class ItemsLayout(ElementsLayoutBase):
    """아이템 목록을 관리하는 레이아웃 객체.
    아이템 중앙을 기준으로 좌표를 계산함."""
    def __init__(
            self, 
            scene: Scene, 
            length: int,
            space: int = 150,
            y: int = 0,
            height: int = 300,
            ) -> None:
        """ItemsLayout의 초기화 함수.
        params:
            `scene`: Scene - 이 객체가 존재하는 Scene.
            `length`: int - 보유한 아이템 수.
            `space`: int - 아이템의 기준점에서 인접 아이템의 기준점까지의 거리.
            `y`: int - 창 하단에서부터의 y좌표.
            `height`: int - 레이아웃의 세로 길이. 스크롤 시 커서 위치 검사에 사용."""
        super().__init__(scene, length)
        self.space: int = space
        self.y: int = y
        self.height: int = height

    def get_width(self) -> int:
        """가장 왼쪽 아이템의 기준점부터 가장 오른쪽 아이템 기준점까지의 거리 계산.
        화면비에 영향을 받지 않는 값."""
        return self.space * (self.length-1)
    
    def get_position(self, index: int, scaled: bool = True) -> Vec2:
        result: Vec2 = Vec2((self.scene.ref_w-self.get_width())/2 + index*self.space, self.y) 
        if scaled:
            result *= self.scene.scale_factor
        return result
    
    def get_rotation(self, index: int) -> float:
        return 0.0
    
    def get_scale(self, index: int) -> float:
        return 1.0