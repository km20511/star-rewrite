from typing import Final

import pyglet
from pyglet.math import Vec2
from pyglet.sprite import Sprite

from gui.scenes.scene import Scene

ICON_DEFALUT: Final[str] = "icon_coin.png"
ICON_COIN: Final[str] = "icon_coin.png"
ICON_ATTACK: Final[str] = "icon_attack.png"
ICON_HEALTH: Final[str] = "icon_health.png"
ICON_ACTION: Final[str] = "icon_action.png"
ICON_TURN: Final[str] = "icon_turn.png"
PLACEHOLDER: Final[str] = "ui_placeholder.png"

STAT_FONT: Final[str] = "Neo둥근모 Pro"

class PlayerHUD:
    """플레이어의 정보(턴 수, 가진 돈, 공격력 등)를 출력하는 UI."""
    def __init__(
            self, 
            scene: Scene,
            player_money: int,
            player_health: int, 
            player_attack: int,
            player_action: int,
            player_remaining_action: int,
            current_turn: int,
            width: int,
            height: int,
            space: int,
            bottom_left: Vec2
            ) -> None:
        self.scene: Scene = scene
        self.val_money: int = player_money
        self.val_health: int = player_health
        self.val_attack: int = player_attack
        self.val_action: int = player_action
        self.val_remaining_action: int = player_remaining_action
        self.val_turn: int = current_turn

        img_placeholder = pyglet.resource.image(PLACEHOLDER)
        try: img_coin = pyglet.resource.image(ICON_COIN)
        except pyglet.resource.ResourceNotFoundException: img_coin = pyglet.resource.image(ICON_DEFALUT)
        try: img_atttack = pyglet.resource.image(ICON_ATTACK)
        except pyglet.resource.ResourceNotFoundException: img_coin = pyglet.resource.image(ICON_DEFALUT)
        try: img_health = pyglet.resource.image(ICON_HEALTH)
        except pyglet.resource.ResourceNotFoundException: img_coin = pyglet.resource.image(ICON_DEFALUT)
        try: img_action = pyglet.resource.image(ICON_ACTION)
        except pyglet.resource.ResourceNotFoundException: img_coin = pyglet.resource.image(ICON_DEFALUT)
        try: img_turn = pyglet.resource.image(ICON_ACTION)
        except pyglet.resource.ResourceNotFoundException: img_coin = pyglet.resource.image(ICON_DEFALUT)

        self.sprite_placeholder = Sprite(img_placeholder)