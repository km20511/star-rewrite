from typing import Final

import pyglet
from pyglet.math import Vec2

from core import GameManager
from core.enums import CardType
from gui.anchored_widget import AnchorPreset
from gui.buttons import SolidButton, SolidButtonState
from gui.card import Card
from gui.color import Color
from gui.elements_layout import CardsLayout
from gui.player_hud import PlayerHUD
from gui.scenes import Scene

CONTENTS_FONT: Final[str] = "Neo둥근모 Pro"

class MainScene(Scene):
    def load(self):
        super().load()

        filepath = self.context.file_path
        assert filepath != "", "파일 경로가 설정되지 않았습니다."

        self.game: GameManager = GameManager.create_from_file(filepath)
        self.game_state = self.game.get_game_draw_state()

        self.bg_sprite = pyglet.sprite.Sprite(pyglet.resource.image("background.png"))

        self.ui_batch = pyglet.graphics.Batch()
        self.ui_group = pyglet.graphics.Group(order=5)

        self.card_batch = pyglet.graphics.Batch()
        self.card_group = pyglet.graphics.Group(order=3)
        self.card_thumnail_group = pyglet.graphics.Group(order=2)
        self.card_text_group = pyglet.graphics.Group(order=4)
        self.frame_display = pyglet.window.FPSDisplay(window=self.window)

        self.setup_scene()

        def on_window_resized(w: int, h: int):
            self.bg_sprite.scale_x, self.bg_sprite.scale_y = self.scale_factor_x, self.scale_factor_y
        self.push_handlers(on_scene_window_resized=on_window_resized)
        
        @self.window.event
        def on_draw():
            self.window.clear()
            self.bg_sprite.draw()
            self.card_batch.draw()
            self.ui_batch.draw()
            # self.frame_display.draw()

    def setup_scene(self):
        """GameDrawState를 이용해 게임 상태 초기화."""

        self.hud = PlayerHUD(
            self,
            self.game_state.player_money, self.game_state.player_health,
            self.game_state.player_attack, self.game_state.player_action,
            self.game_state.player_remaining_action, self.game_state.current_turn,
            160, 80, 20, Vec2(20, 20),
            batch=self.ui_batch, ui_group=self.ui_group)
        
        self.card_layout = CardsLayout(
            self, len(self.game_state.deck),
            center_scale=1.4,
            scale_width=0.4,
            selected=0,
            scroll_sensitivity=7.0
        )

        self.cards = [Card(data, self.card_layout, self.card_batch, self.card_group, self.card_thumnail_group, self.card_text_group, index=index)
                    for index, data in enumerate(self.game_state.deck)]

        self.buy_button = SolidButton(
            self, x=0, y=100, width=200, height=50, border=3, 
            text="구매", font_family="Neo둥근모 Pro", font_size=20,
            pressed=SolidButtonState(
                box_color=Color.white(), border_color=Color.white(),
                label_color=Color.black(), transition=0.3
            ),
            depressed=SolidButtonState(
                box_color=Color.black(), border_color=Color.white(),
                label_color=Color.white(), transition=0.3
            ),
            hover=SolidButtonState(
                box_color=Color.white(), border_color=Color.white(),
                label_color=Color.black(), transition=0.3
            ),
            disenabled=SolidButtonState(
                box_color=Color.white()*0.6, border_color=Color.white()*0.6,
                label_color=Color.black(), transition=0.3
            ),
            anchor=AnchorPreset.BottomCenter,
            pivot=AnchorPreset.BottomCenter,
            scale_factor=self.scale_factor,
            batch=self.ui_batch, group=self.ui_group
        )

        self.card_layout.push_handlers(on_selection_changed=lambda index: self.buy_button.set_enabled(self._check_purchasable(index)))
        self.buy_button.set_enabled(self._check_purchasable(0))

    def _check_purchasable(self, index: int) -> bool:
        """카드가 구매 가능한지 확인."""
        if not (0 <= index < len(self.game_state.deck)):
            return False
        card = self.game_state.deck[index]
        if not card.is_front_face or self.game_state.player_remaining_action <= 0:
            return False
        return (self.game_state.player_health + self.game_state.player_attack >= card.current_cost
                if card.type == CardType.Enemy
                else self.game_state.player_money >= card.current_cost)
