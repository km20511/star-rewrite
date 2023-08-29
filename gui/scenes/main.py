from typing import Final

import pyglet

from core import GameManager
from gui.card import Card
from gui.color import Color
from gui.elements_layout import CardsLayout
from gui.scenes import Scene

CONTENTS_FONT: Final[str] = "Neo둥근모 Pro"

class MainScene(Scene):
    def load(self):
        super().load()

        filepath = self.context.file_path
        assert filepath != "", "파일 경로가 설정되지 않았습니다."

        self.game: GameManager = GameManager.create_from_file(filepath)
        self.game_state = self.game.get_game_draw_state()

        self.bg_shape = pyglet.shapes.Rectangle(
            0,0,self.window.width, self.window.height,
            (Color.white() * 0.4).tuple_256())

        self.ui_batch = pyglet.graphics.Batch()
        self.ui_group = pyglet.graphics.Group(order=5)

        self.card_batch = pyglet.graphics.Batch()
        self.card_group = pyglet.graphics.Group(order=3)
        self.card_thumnail_group = pyglet.graphics.Group(order=2)
        self.card_text_group = pyglet.graphics.Group(order=4)
        self.frame_display = pyglet.window.FPSDisplay(window=self.window)

        self.setup_scene()
        
        @self.window.event
        def on_draw():
            self.window.clear()
            self.card_batch.draw()
            self.ui_batch.draw()
            self.frame_display.draw()

    def setup_scene(self):
        """GameDrawState를 이용해 게임 상태 초기화."""
        self.hud_document = pyglet.text.Label(
            f"{self.game_state.current_turn} 턴\n돈: {self.game_state.player_money}\n"
            f"체력: {self.game_state.player_health}\n공격력: {self.game_state.player_attack}\n"
            f"남은 행동: {self.game_state.player_remaining_action} / {self.game_state.player_action}",
            CONTENTS_FONT, 20,
            x=20, y=self.window.height -20, width=300,
            anchor_x="left", anchor_y="top", align="left",
            multiline=True,
            batch=self.ui_batch,
            group=self.ui_group
        )
        
        self.card_layout = CardsLayout(
            self, len(self.game_state.deck),
            center_scale=1.4,
            scale_width=0.4,
            scroll_sensitivity=5.0
        )

        self.cards = [Card(data, self.card_layout, self.card_batch, self.card_group, self.card_thumnail_group, self.card_text_group, index=index)
                    for index, data in enumerate(self.game_state.deck)]