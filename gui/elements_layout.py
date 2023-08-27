from pyglet.math import Vec2

from gui.scenes import Scene
from gui.utils import clamp, lerp

class ElementsLayoutBase:
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
            `scroll_sensitivity`: float - 스크롤 속력."""
        super().__init__(scene, length)
        self.space: int = space
        self.y: int = y
        self.height: int = height
        self.center_scale: float = center_scale
        self.scale_width: float = scale_width
        self.scroll_value: float = initial_scroll
        self.scroll_sensitivity: float = scroll_sensitivity

        @self.scene.window.event
        def on_scroll(x: int, y: int, scroll_x: float, scroll_y: float):
            if abs(y - (self.scene.window.height + self.y*self.scene.scale_factor)) > self.height // 2:
                return
            self.scroll_value = clamp(
                self.scroll_value + (scroll_x + scroll_y) * self.scroll_sensitivity,
                0, self.get_width()
            )

    def get_position(self, index: int) -> Vec2:
        return Vec2(self.space*index - self.scroll_value, self.y) * self.scene.scale_factor + Vec2(0, self.scene.window.height // 2)
    
    def get_rotation(self, index: int) -> float:
        return 0.0
    
    def get_scale(self, index: int) -> float:
        pos_x: float = self.get_position(index).x
        normal_x: float = pos_x / self.scene.window.width
        if abs(normal_x - 0.5)*2 > self.scale_width:
            return self.scene.scale_factor
        return lerp(self.center_scale, 1.0, abs(normal_x - 0.5)) * self.scene.scale_factor

    def get_width(self) -> int:
        """가장 왼쪽 카드의 기준점부터 가장 오른쪽 카드 기준점까지의 거리 계산.
        화면비에 영향을 받지 않는 값."""
        return self.space * (self.length-1)
    

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
        """CardsLayout의 초기화 함수.
        params:
            `scene`: Scene - 이 객체가 존재하는 Scene.
            `length`: int - 보유한 카드 수.
            `space`: int - 카드의 기준점에서 인접 카드의 기준점까지의 거리.
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
    
    def get_position(self, index: int) -> Vec2:
        return Vec2((self.scene.ref_w-self.get_width())/2 + index*self.space, self.y) * self.scene.scale_factor
    
    def get_rotation(self, index: int) -> float:
        return 0.0
    
    def get_scale(self, index: int) -> float:
        return 1.0