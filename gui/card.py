import time
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

from gui.transitions import Transition

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
            group_body: Group,
            group_thumbnail: Group,
            group_text: Group,
            height: float = 240.0,
            index: int = 0
            ) -> None:
        self.data: CardDrawData = data
        self.layout: CardsLayout = layout
        self.batch: Batch = batch
        self.group_body: Group = group_body
        self.group_thumbnail: Group = group_thumbnail
        self.group_text: Group = group_text
        self.base_width: float = height / 1.5
        self.base_height: float = height
        self.index: int = index
        self.transform = Transform2D(
            layout.get_position(index),
            layout.get_rotation(index),
            Vec2(1, 1) * layout.get_scale(index)
        )
        self.transition = Transition[Transform2D](self.transform, self.transform, 0.5)

        image_front = pyglet.resource.image(CARD_SPRITE[data.type][0])
        try:
            image_content = pyglet.resource.image(data.sprite_name)
        except pyglet.resource.ResourceNotFoundException:
            image_content = pyglet.resource.image("card_unknown.png")
        image_back = pyglet.resource.image(CARD_SPRITE[data.type][1])

        image_front.anchor_x = image_front.width / 2
        image_front.anchor_y = image_front.height / 2
        image_content.anchor_x = image_content.width / 2
        image_content.anchor_y = image_content.height / 2
        image_back.anchor_x = image_back.width / 2
        image_back.anchor_y = image_back.height / 2

        self.sprite_front = Sprite(image_front, z=2, batch=batch, group=group_body)
        self.sprite_content = Sprite(image_content, z=1, batch=batch, group=group_thumbnail)
        self.sprite_back = Sprite(image_back, z=2, batch=batch, group=group_body)

        
        self.label_cost = pyglet.text.Label(
            str(data.current_cost), 
            font_name=COST_FONT, font_size=15,
            anchor_x="center", anchor_y="center", align="center", z=3, 
            batch=batch, group=group_text
        )
        self.label_title = pyglet.text.Label(
            data.name, 
            font_name=TITLE_FONT, font_size=10,
            color=Color.black().tuple_256(),
            anchor_x="center", anchor_y="center", align="center", z=3, 
            batch=batch, group=group_text
        )
        self.label_description = pyglet.text.Label(
            data.description, 
            font_name=TITLE_FONT, font_size=8,
            color=Color.black().tuple_256(),
            anchor_x="center", anchor_y="center", align="center", z=3, 
            width=self.base_width / 1.5 * layout.scene.scale_factor, multiline=True,
            batch=batch, group=group_text
        )

        self.layout.push_handlers(on_layout_modified=lambda : self.update_state())
        self.layout.scene.push_handlers(on_scene_updated=self._update_transition)
        self.update_state()
    
    def _update_transition(self, dt: float):
        if self.transition.active:
            self.transform = self.transition.update(time.time())

    def update_state(self):
        """현재 데이터를 기준으로 상태를 갱신."""
        self.transform = Transform2D(
            self.layout.get_position(self.index),
            self.layout.get_rotation(self.index),
            Vec2(1, 1) * self.layout.get_scale(self.index)
        ) if not self.transition.active else self.transition.update(time.time())
        trs = self.transform.matrix

        if self.data.is_front_face:
            self.sprite_back.visible = False
            self.sprite_front.visible = self.sprite_front.visible = True
            self.label_title.visible = self.label_description.visible = True
            self.label_cost.visible = self.data.type != CardType.Event

            # translation이 제대로 이루어지려면 z=1인 3차원 벡터 필요.
            self.sprite_content.position = (*(trs @ (Vec3(0, self.base_height * 42.5 / 180, 1)))[:2], 1)
            self.sprite_content.rotation = self.transform.rotation
            self.sprite_content.width, self.sprite_content.height = self.base_width*100/120*self.transform.scale.x, self.base_height*75/180*self.transform.scale.y

            self.sprite_front.position = (*self.transform.position, 2)
            self.sprite_front.rotation = self.transform.rotation
            self.sprite_front.width, self.sprite_front.height = self.base_width*self.transform.scale.x, self.base_height*self.transform.scale.y
            
            if self.data.type != CardType.Event:
                self.label_cost.position = (*(trs @ (Vec3(-self.base_width * 45 / 120, self.base_height * 75 / 180, 1)))[:2], 3)
                self.label_cost.rotation = self.transform.rotation
                self.label_cost.font_size = 15 * self.transform.scale.x
                self.label_cost.color = (
                    Color.black() if self.data.base_cost == self.data.current_cost else (
                        Color.green() if (self.data.type == CardType.Enemy ^ self.data.current_cost > self.data.base_cost)
                        else Color.red()
                    )
                ).tuple_256()
            
            self.label_title.position = (*(trs @ (Vec3(0, self.base_height * 0, 1)))[:2], 3)
            self.label_title.rotation = self.transform.rotation
            self.label_title.font_size = 10 * self.transform.scale.x

            self.label_description.position = (*(trs @ (Vec3(0, -self.base_height * 0.25, 1)))[:2], 3)
            self.label_description.rotation = self.transform.rotation
            self.label_description.width = self.transform.scale.x * self.base_width / 1.2
            self.label_description.font_size = 8 * self.transform.scale.x
        else:
            self.sprite_front.visible = self.sprite_content.visible = False
            self.label_cost.visible = self.label_title.visible = self.label_description.visible = False
            self.sprite_back.visible = True

            self.sprite_back.position = (*self.transform.position, 2)
            self.sprite_back.rotation = self.sprite_back.rotation
            self.sprite_back.width, self.sprite_back.height = self.base_width*self.transform.scale.x, self.base_height*self.transform.scale.y
    
    def set_front_face(self, is_front_face: bool):
        """앞/뒷면 설정."""
        self.data.is_front_face = is_front_face
        self.update_state()

    def move_to(self, new_index: int, duration: float = 0.5):
        """주어진 인덱스로 이동함."""
        if duration < 0.05:
            # 전이를 수행하지 않음.
            self.index = new_index
            self.update_state()
            return
        self.transition.start_value = self.transform
        self.transition.destination_value = Transform2D(
            self.layout.get_position(new_index),
            self.layout.get_rotation(new_index),
            self.layout.get_scale(new_index)
        )
        self.transition.start(time.time(), duration)

    def set_cost(self, new_cost: int):
        """표시되는 비용을 변경."""
        if self.data.type == CardType.Event: return
        if (delta := new_cost - self.data.base_cost) == 0:
            self.label_cost.color = Color.black().tuple_256()
        elif delta > 0 ^ self.data.type == CardType.Item:
            self.label_cost.color = Color.green().tuple_256()
        else:
            self.label_cost.color = Color.red().tuple_256()
        self.label_cost.text = str(new_cost)
        self.update_state()

    def delete(self):
        """이 카드를 파괴함."""
        raise NotImplementedError