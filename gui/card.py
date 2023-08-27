from typing import Dict, Final, Tuple

import pyglet
from pyglet.math import Vec2, Vec3

from core.enums import CardType
from core.obj_data_formats import CardDrawData
from gui.color import Color
from gui.elements_layout import CardsLayout
from gui.transform import Transform2D
from pyglet.graphics import Batch, Group
from pyglet.sprite import Sprite

CARD_SPRITE: Final[Dict[CardType, Tuple[str, str]]] = {
    CardType.Enemy: ("card_enemy_front.png", "card_enemy_back.png"),
    CardType.Event: ("card_event_front.png", "card_event_back.png"),
    CardType.Item: ("card_item_front.png", "card_item_back.png"),
}
COST_FONT: Final[str] = "Algerian"
TITLE_FONT: Final[str] = "Neo둥근모 Pro"
CONTENT_FONT: Final[str] = "Neo둥근모 Pro"

class Card:
    """게임 화면에 그려지는 카드 객체."""
    def __init__(
            self, 
            data: CardDrawData, 
            layout: CardsLayout,
            batch: Batch,
            group: Group,
            height: float = 240.0,
            index: int = 0
            ) -> None:
        self.data: CardDrawData = data
        self.layout: CardsLayout = layout
        self.batch: Batch = batch
        self.group: Group = group
        self.base_width: float = height / 1.5
        self.base_height: float = height
        self.index: int = index
        self.transform = Transform2D(
            layout.get_position(index),
            layout.get_rotation(index),
            Vec2(1, 1) * layout.get_scale(index)
        )

        self.sprite_front = Sprite(pyglet.resource.image(CARD_SPRITE[data.type][0]), z=2, batch=batch, group=group)
        try:
            self.sprite_content = Sprite(pyglet.resource.image(data.sprite_name), z=1, batch=batch, group=group)
        except pyglet.resource.ResourceNotFoundException:
            self.sprite_content = Sprite(pyglet.resource.image("card_unknown.png"))
        self.sprite_back = Sprite(pyglet.resource.image(CARD_SPRITE[data.type][1]), z=2, batch=batch, group=group)

        self.sprite_front.image.anchor_x = self.sprite_front.image.width / 2
        self.sprite_front.image.anchor_y = self.sprite_front.image.height / 2
        self.sprite_content.image.anchor_x = self.sprite_content.image.width / 2
        self.sprite_content.image.anchor_y = self.sprite_content.image.height / 2
        self.sprite_back.image.anchor_x = self.sprite_back.image.width / 2
        self.sprite_back.image.anchor_y = self.sprite_back.image.height / 2
        
        self.label_cost = pyglet.text.Label(
            str(data.current_cost), 
            font_name=COST_FONT, font_size=15,
            anchor_x="center", anchor_y="center", align="center", z=3, 
            batch=batch, group=group
        )
        self.label_title = pyglet.text.Label(
            data.name, 
            font_name=TITLE_FONT, font_size=15,
            color=Color.black().tuple_256(),
            anchor_x="center", anchor_y="center", align="center", z=3, 
            batch=batch, group=group
        )
        self.label_description = pyglet.text.Label(
            data.name, 
            font_name=TITLE_FONT, font_size=15,
            color=Color.black().tuple_256(),
            anchor_x="center", anchor_y="center", align="center", z=3, 
            width=self.base_width / 1.5 * layout.scene.scale_factor, multiline=True,
            batch=batch, group=group
        )

        self.layout.scene.push_handlers(on_scene_updated=lambda dt: self.update_state())
        self.update_state()

    def update_state(self):
        """현재 데이터를 기준으로 상태를 갱신."""
        self.transform = Transform2D(
            self.layout.get_position(self.index),
            self.layout.get_rotation(self.index),
            Vec2(1, 1) * self.layout.get_scale(self.index)
        )
        trs = self.transform.matrix

        if self.data.is_front_face:
            self.sprite_back.visible = False
            self.sprite_front.visible = self.sprite_front.visible = True
            self.label_title.visible = self.label_description.visible = True
            self.label_cost.visible = self.data.type != CardType.Event

            self.sprite_content.position = (*(trs @ (Vec3(0, self.base_height * 42.5 / 180)))[:2], 1)
            self.sprite_content.rotation = self.transform.rotation
            self.sprite_content.width, self.sprite_content.height = self.base_width*self.transform.scale.x, self.base_height*self.transform.scale.y

            self.sprite_front.position = (*self.transform.position, 2)
            self.sprite_front.rotation = self.transform.rotation
            self.sprite_front.width, self.sprite_front.height = self.base_width*self.transform.scale.x, self.base_height*self.transform.scale.y
            
            if self.data.type != CardType.Event:
                self.label_cost.position = (*(trs @ (Vec3(-self.base_width * 45 / 120, self.base_height * 75 / 180)))[:2], 3)
                self.label_cost.rotation = self.transform.rotation
                self.label_cost.font_size = 15 * self.transform.scale.x
                self.label_cost.color = (
                    Color.white() if self.data.base_cost == self.data.current_cost else (
                        Color.green() if (self.data.type == CardType.Enemy ^ self.data.current_cost > self.data.base_cost)
                        else Color.red()
                    )
                ).tuple_256()
            
            self.label_title.position = (*(trs @ (Vec3(0, self.base_height * 0)))[:2], 3)
            self.label_title.rotation = self.transform.rotation
            self.label_title.font_size = self.transform.scale.x

            self.label_description.position = (*(trs @ (Vec3(0, -self.base_height * 0.25)))[:2], 3)
            self.label_description.rotation = self.transform.rotation
            self.label_description.width = self.transform.scale.x * self.base_width / 1.5
            self.label_description.font_size = self.transform.scale.x
        else:
            self.sprite_front.visible = self.sprite_content.visible = False
            self.label_cost.visible = self.label_title.visible = self.label_description.visible = False
            self.sprite_back.visible = True

            self.sprite_back.position = (*self.transform.position, 2)
            self.sprite_back.rotation = self.sprite_back.rotation
            self.sprite_back.width, self.sprite_back.height = self.base_width*self.transform.scale.x, self.base_height*self.transform.scale.y