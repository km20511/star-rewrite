import pyglet

from gui.scene import Scene


class IntroScene(Scene):
    """게임 실행 시 보여지는 타이틀 화면."""

    def load(self):
        raise NotImplementedError
    
    def unload(self):
        return NotImplementedError