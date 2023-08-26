from enum import Enum, auto
import json
import os
from typing import Callable, Final, List, Tuple

import pyglet

from gui.color import Color
from gui.scenes.scene import Scene
from gui.buttons import SolidButton, SolidButtonState


TITLE_FONT: Final[str] = "Algerian"
CONTENT_FONT: Final[str] = "Neo둥근모 Pro"

LEVEL_PATH: Final[str] = "data/levels"
SAVES_PATH: Final[str] = "data/saves"

class IntroScene(Scene):
    """게임 실행 시 보여지는 타이틀 화면."""

    match_w_h = 0.7
    ref_w: int = 1280
    ref_h: int = 720
    on_load_file: Callable[[str], None] = lambda x: None

    class UIState(Enum):
        Title = auto()
        Selecting = auto()
    ui_state: UIState = UIState.Title

    def load(self, on_load_file: Callable[[str], None]):
        super().load()

        self.ui_state = IntroScene.UIState.Title
        self.title_batch = pyglet.graphics.Batch()
        self.selection_batch = pyglet.graphics.Batch()

        self.title_text = pyglet.text.Label(
            "Star Rewrite",
            font_name=TITLE_FONT,
            font_size=45,
            bold=True,
            x=self.window.width // 2,
            y=self.window.height // 2 + 100,
            anchor_x="center",
            anchor_y="center",
            batch=self.title_batch
        )

        btn_depressed = SolidButtonState(
            box_color=Color.black(),
            border_color=Color.white(),
            label_color=Color.white(),
            transition=1.0
        )
        btn_pressed = SolidButtonState(
            box_color=Color.white(),
            border_color=Color.white(),
            label_color=Color.black(),
            transition=1.0
        )
        btn_hover = SolidButtonState(
            box_color=Color.white(),
            border_color=Color.white(),
            label_color=Color.black(),
            transition=1.0
        )
        self.group_btn = pyglet.graphics.Group(order=3)
        self.btn_style = {
            "width": 300,
            "height": 80,
            "border": 5,
            "font_family": CONTENT_FONT,
            "font_size": 20,
            "pressed": btn_pressed,
            "depressed": btn_depressed,
            "hover": btn_hover,
            "batch": self.title_batch,
            "group": self.group_btn
        }

        button_y_1: int = -100
        button_y_step: int = -100

        self.title_btns: List[SolidButton] = [
            SolidButton(
                scene=self,
                x=self.window.width // 2 - 150,
                y=self.window.height // 2 + button_y_1 + button_y_step*ind,
                text=text,
                **self.btn_style
            ) for ind, text in enumerate(("이어 하기", "새 게임 생성"))
        ]
        self.title_btns[0].push_handlers(on_press=lambda : self.select_menu(True))
        self.title_btns[1].push_handlers(on_press=lambda : self.select_menu(False))

        self.level_select_text = pyglet.text.Label(
            "",
            font_name=TITLE_FONT,
            font_size=45,
            bold=True,
            x=self.window.width // 2,
            y=self.window.height // 2 + 100,
            anchor_x="center",
            anchor_y="center",
            batch=self.selection_batch
        )


        @self.window.event
        def on_draw():
            self.window.clear()
            if self.ui_state == IntroScene.UIState.Title:
                self.title_batch.draw()
            else:
                self.selection_batch.draw()

    def select_menu(self, is_savefile: bool):
        """is_savefile이 참이면 저장 파일을, 거짓이면 레벨을 선택하는 화면 구성."""
        self.level_select_text.text = "Continue" if is_savefile else "New Game"
        btn_texts_and_paths: List[Tuple[str, str]] = []
        self.ui_state = IntroScene.UIState.Selecting
    
        if is_savefile:
            for filename in os.listdir(SAVES_PATH):
                if not filename.endswith(".json"):
                    continue
                with open(os.path.join(SAVES_PATH, filename), encoding="utf-8") as f:
                    tree = json.load(f)
                    btn_texts_and_paths.append((
                        " ".join((tree["level_name"], f"{tree['current_turn']}", tree["datetime"])),
                        os.path.join(SAVES_PATH, filename)
                    ))
        else:
            for filename in os.listdir(LEVEL_PATH):
                if not filename.endswith(".json"):
                    continue
                with open(os.path.join(LEVEL_PATH, filename), encoding="utf-8") as f:
                    tree = json.load(f)
                    btn_texts_and_paths.append((
                        tree["level_name"],
                        os.path.join(LEVEL_PATH, filename)
                    ))

        button_y_1: int = -100
        button_y_step: int = -100
        self.selection_btns: List[SolidButton] = []
        for ind, (text, filename) in enumerate(btn_texts_and_paths):
            btn = SolidButton(
                scene=self,
                x=self.window.width // 2 - 150,
                y=self.window.height // 2 + button_y_1 + button_y_step*ind,
                text=text,
                **(self.btn_style | {"batch": self.selection_batch})
            )
            btn.push_handlers(on_press=lambda file=filename: self.on_load_file(file))

    def on_resize_window(self, w: int, h: int) -> None:
        super().on_resize_window(w, h)

        self.title_text.font_size = 45 * self.scale_factor
        self.title_text.x = self.window.width//2
        self.title_text.y = self.window.height//2 + 100*self.scale_factor
    
    def unload(self):
        return NotImplementedError