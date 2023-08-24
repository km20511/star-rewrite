import pyglet


class Scene:
    """게임에서 사용할 장면의 부모 클래스. 인트로(게임 선택), 메인 화면 등이 예."""

    def __init__(self, window: pyglet.window.Window) -> None:
        self.window = window

    def load(self):
        """저장된 Window 객체에서 Scene을 구성함."""

    def unload(self):
        """저장된 Window 객체에서 이 Scene을 삭제. 다른 Scene으로 전환하기 전 호출할 것."""
