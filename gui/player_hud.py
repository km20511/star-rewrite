from enum import Enum, auto
from typing import Dict, Final, List

import pyglet
from pyglet.math import Vec2
from pyglet.text import Label
from pyglet.sprite import Sprite
from pyglet.graphics import Batch, Group

from gui.scenes.scene import Scene

class HUDValueType(Enum):
    """HUD에 출력할 데이터의 종류."""
    Turn = auto()
    Money = auto()
    Health = auto()
    Attack = auto()
    Action = auto()

ICON_DEFALUT: Final[str] = "icon_coin.png"
ICON_TABLE: Final[Dict[HUDValueType, str]] = {
    HUDValueType.Turn: "icon_turn.png",
    HUDValueType.Money: "icon_coin.png",
    HUDValueType.Health: "icon_health.png",
    HUDValueType.Attack: "icon_attack.png",
    HUDValueType.Action: "icon_action.png",
}
PLACEHOLDER: Final[str] = "ui_placeholder.png"

STAT_FONT: Final[str] = "Neo둥근모 Pro"

FONT_SIZE: Final[int] = 22
ICON_SIZE: Final[int] = 30
ICON_OFFSET: Final[Vec2] = Vec2(20, 1)
LABEL_OFFSET: Final[Vec2] = Vec2(15, 0)

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
            top_left: Vec2,
            batch: Batch,
            ui_group: Group
            ) -> None:
        self.scene: Scene = scene
        self.batch: Batch = batch
        self.group_placeholder: Group = ui_group
        self.group_content: Group = Group(order=ui_group.order+1, parent=ui_group)
        self.val_money: int = player_money
        self.val_health: int = player_health
        self.val_attack: int = player_attack
        self.val_action: int = player_action
        self.val_remaining_action: int = player_remaining_action
        self.val_turn: int = current_turn
        self.ui_width: int = width
        self.ui_height: int = height
        self.ui_space: int = space
        self.top_left: Vec2 = top_left

        img_placeholder = pyglet.resource.image(PLACEHOLDER)
        img_placeholder.width, img_placeholder.height = width, height

        text: Dict[HUDValueType, str] = {
            HUDValueType.Turn: f"{self.val_turn}턴",
            HUDValueType.Money: str(self.val_money),
            HUDValueType.Health: str(self.val_health),
            HUDValueType.Attack: str(self.val_attack),
            HUDValueType.Action: f"{self.val_remaining_action}/{self.val_action}"
        }

        self.icon_sprites: Dict[HUDValueType, Sprite] = {}
        self.labels: Dict[HUDValueType, Label] = {}

        for val_type in HUDValueType:
            try:
                img_icon = pyglet.resource.image(ICON_TABLE[val_type])
            except pyglet.resource.ResourceNotFoundException:
                img_icon = pyglet.resource.image(ICON_DEFALUT)
            img_icon.width, img_icon.height = Vec2(1,1) * ICON_SIZE
            img_icon.anchor_x, img_icon.anchor_y = 0, img_icon.height / 2
            self.icon_sprites[val_type] = Sprite(img_icon, batch=batch, group=self.group_content)    
            self.labels[val_type] = Label(
                text=text[val_type],
                font_name=STAT_FONT, color=(0,0,0,255), font_size=FONT_SIZE,
                anchor_x="left", anchor_y="center", align="right",
                batch=batch, group=self.group_content
            )
        self.placeholder_sprites: List[Sprite] = [Sprite(img_placeholder, batch=batch, group=self.group_placeholder) for i in range(5)]
        
        self.update_layout()

        self.scene.push_handlers(on_scene_window_resized=lambda w,h: self.update_layout())

    def update_layout(self):
        """가지고 있는 정보를 기반으로 HUD를 배치."""
        for i, val_type in enumerate(HUDValueType):
            top_left: Vec2 = Vec2(self.ui_space + self.ui_width, 0)*i + self.top_left
            bottom_left: Vec2 = Vec2(top_left.x, self.scene.ref_h - (top_left.y + self.ui_height))
            self.placeholder_sprites[i].position = *(bottom_left*self.scene.scale_factor), 0
            self.placeholder_sprites[i].scale = self.scene.scale_factor
            self.icon_sprites[val_type].position = *((bottom_left + Vec2(0, self.ui_height/2) + ICON_OFFSET)*self.scene.scale_factor), 0
            self.icon_sprites[val_type].scale = self.scene.scale_factor
            self.labels[val_type].position = *((bottom_left + Vec2(0, self.ui_height/2) + LABEL_OFFSET)*self.scene.scale_factor), 0
            self.labels[val_type].width = (self.ui_width - ICON_SIZE)*self.scene.scale_factor
            self.labels[val_type].font_size = FONT_SIZE*self.scene.scale_factor