from typing import Final
import pyglet

from gui.scenes.scene import Scene


TITLE_FONT: Final[str] = "Algerian"
CONTENT_FONT: Final[str] = "Neo둥근모 Pro"

class IntroScene(Scene):
    """게임 실행 시 보여지는 타이틀 화면."""

    match_w_h = 0.7
    ref_w: int = 1280
    ref_h: int = 720

    def load(self):
        super().load()

        self.batch = pyglet.graphics.Batch()

        self.title_text = pyglet.text.Label(
            "Star Rewrite",
            font_name=TITLE_FONT,
            font_size=45,
            bold=True,
            x=self.window.width // 2,
            y=self.window.height // 2 + 100,
            anchor_x="center",
            anchor_y="center",
            batch=self.batch
        )
        self.continue_btn = pyglet.gui.PushButton()

        @self.window.event
        def on_draw():
            self.window.clear()
            self.batch.draw()

    def on_resize_window(self, w: int, h: int) -> None:
        super().on_resize_window(w, h)

        self.title_text.font_size = 45 * self.scale_factor
        self.title_text.x = self.window.width//2
        self.title_text.y = self.window.height//2 + 100*self.scale_factor
    
    def unload(self):
        return NotImplementedError