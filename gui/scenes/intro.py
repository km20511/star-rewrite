from enum import Enum, auto
import json
import os
from typing import Any, Callable, Final, List, Tuple

import pyglet
from pyglet.text import Label
from gui.anchored_widget import AnchorPreset

from gui.color import Color
from gui.game_context import GameContext
from gui.scenes.scene import Scene
from gui.buttons import SolidButton, SolidButtonState


TITLE_FONT: Final[str] = "Algerian"
TITLE_FONT_SIZE: Final[int] = 65
TITLE_OFFSET_Y: Final[int] = 100
CONTENT_FONT: Final[str] = "Neo둥근모 Pro"
CONTENT_FONT_SIZE: Final[int] = 20
BUTTON_MIN_WIDTH: Final[int] = 400
BUTTON_TEXT_PIVOT: Final[int] = 20

LEVEL_PATH: Final[str] = "data/levels"
SAVES_PATH: Final[str] = "data/saves"

class IntroScene(Scene):
    """게임 실행 시 보이는 타이틀 화면."""

    match_w_h = 0.7
    ref_w: int = 1280
    ref_h: int = 720

    
    def load(self):
        """메뉴 선택 Scene을 불러옴."""
        super().load()

        self.batch = pyglet.graphics.Batch()
        self.group = pyglet.graphics.Group(order=0)

        self.title_text = Label(
            "Star Rewrite",
            font_name=TITLE_FONT, font_size=TITLE_FONT_SIZE*self.scale_factor,
            color=Color.white().tuple_256(),
            x=self.window.width//2, y=self.window.height//2+TITLE_OFFSET_Y*self.scale_factor,
            anchor_x="center", anchor_y="center", align="center",
            batch=self.batch, group=self.group
        )

        self._btn_args = dict(
            scene=self, width=400, height=80,
            border=4, font_family=CONTENT_FONT, font_size=CONTENT_FONT_SIZE,
            pressed=SolidButtonState(
                box_color=Color.white(), border_color=Color.white(),
                label_color=Color.black(), transition=0.5
            ),
            depressed=SolidButtonState(
                box_color=Color.black(), border_color=Color.white(),
                label_color=Color.white(), transition=0.5
            ),
            hover=SolidButtonState(
                box_color=Color.white(), border_color=Color.white(),
                label_color=Color.black(), transition=0.5
            ), scale_factor=self.scale_factor,
            batch=self.batch, group=self.group
        )

        self.continue_btn = SolidButton(
            text="이어 하기", x=0, y=0, **self._btn_args,
            anchor=AnchorPreset.MiddleCenter, pivot=AnchorPreset.MiddleCenter
        )
        self.newgame_btn = SolidButton(
            text="새로 시작", x=0, y=-100, **self._btn_args,
            anchor=AnchorPreset.MiddleCenter, pivot=AnchorPreset.MiddleCenter
        )

        self.continue_btn.on_press = lambda : self.show_selection(True)
        self.newgame_btn.on_press = lambda : self.show_selection(False)

        self.selection_btns: List[SolidButton] = []


        self.window.push_handlers(on_draw=self._on_draw)
        self.push_handlers(on_scene_window_resized=self._on_scene_window_resized)

    def _on_draw(self):
        self.window.clear()
        self.batch.draw()

    def _on_scene_window_resized(self, w, h):
        self.title_text.font_size = TITLE_FONT_SIZE * self.scale_factor
        self.title_text.x=self.window.width//2
        self.title_text.y=self.window.height//2+TITLE_OFFSET_Y*self.scale_factor
        for btn in self.selection_btns:
            btn.update_layout()

    def show_selection(self, is_savefile: bool):
        """파일 선택 화면을 보임.
        
        is_savefile의 값에 따라 이전 플레이 기록이나 새 스테이지를 보여 줌."""
        self.title_text.text = "Continue" if is_savefile else "New Game"
        self.continue_btn.visible = self.continue_btn.enabled = False
        self.newgame_btn.visible = self.newgame_btn.enabled = False

        label_and_filepath: List[Tuple[str, str]] = []
        if is_savefile:
            for filepath in os.listdir(SAVES_PATH):
                if not filepath.endswith(".json"): continue
                with open(os.path.join(SAVES_PATH, filepath), encoding="utf-8") as f:
                    tree = json.load(f)
                    label_and_filepath.append((
                        f"{tree['level_name']} ({tree['current_turn']}턴) - {tree['datetime']}",
                        os.path.join(SAVES_PATH, filepath)
                    ))
        else:
            for filepath in os.listdir(LEVEL_PATH):
                if not filepath.endswith(".json"): continue
                with open(os.path.join(LEVEL_PATH, filepath), encoding="utf-8") as f:
                    tree = json.load(f)
                    label_and_filepath.append((
                        tree["level_name"],
                        os.path.join(LEVEL_PATH, filepath)
                    ))

        for ind, (text, filepath) in enumerate(label_and_filepath+[("돌아가기", "")]):
            if ind >= len(self.selection_btns):
                self.selection_btns.append(SolidButton(
                    text=text, x=0, y=-100*ind, **self._btn_args
                ))
                self.selection_btns[ind].enabled = False
            btn = self.selection_btns[ind]
            if ind >= len(label_and_filepath):
                btn.on_press = self.return_to_title
            else:
                btn.on_press = lambda filepath=filepath: \
                    self.load_game(filepath)
            btn._label.text = text
            btn.set_base_size(
                base_width=max((btn._label.content_width / self.scale_factor) + BUTTON_TEXT_PIVOT*2, BUTTON_MIN_WIDTH),
                base_height=btn.base_height
            )
            btn.update_layout()

        pyglet.clock.schedule_once(self._show_selection_btn, delay=0.02)

    def return_to_title(self):
        for btn in self.selection_btns:
            btn.visible = btn.enabled = False
        self.title_text.text = "Star Rewrite"
        # 이벤트를 활성과 동시에 받는 것 방지.
        pyglet.clock.schedule_once(self._show_title_btn, delay=0.02)

    def _show_title_btn(self, dt):
        self.continue_btn.visible = self.continue_btn.enabled = True
        self.newgame_btn.visible = self.newgame_btn.enabled = True

    def _show_selection_btn(self, dt):
        for i in self.selection_btns:
            i.visible = i.enabled = True
    
    def load_game(self, filepath):
        self.context.file_path = filepath
        self.context.load_scene("main")

    def unload(self):
        """Scene의 모든 객체 삭제."""
        super().unload()
        self.title_text.delete()
        for btn in self.selection_btns:
            btn.delete()
        self.newgame_btn.delete()
        self.continue_btn.delete()
        self.window.remove_handlers(on_draw=self._on_draw)
        self.remove_handlers(on_scene_window_resized=self._on_scene_window_resized)