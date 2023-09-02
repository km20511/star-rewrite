from typing import Dict, Final, List

import pyglet
from pyglet.math import Vec2
from pyglet.text import Label
from pyglet.sprite import Sprite
from pyglet.shapes import BorderedRectangle
from pyglet.graphics import Batch, Group

from core.obj_data_formats import ItemDrawData
from gui.anchored_widget import AnchorPreset
from gui.buttons import SolidButton, SolidButtonState
from gui.color import Color
from gui.elements_layout import ItemsLayout
from gui.scenes.scene import Scene


ITEM_DEFAULT_ICON: Final[str] = "item_unknown.png"
ITEM_BLANK_ICON: Final[str] = "item_blank_icon.png"
ITEM_INDEX_FONT: Final[str] = "Neo둥근모 Pro"
ITEM_INDEX_FONT_SIZE: Final[int] = 15 
ITEM_INDEX_LABEL_OFFSET: Final[Vec2] = Vec2(0, 10)
ICON_CONTENT_SCALE: Final[float] = 0.7
PAGE_FONT_SIZE: Final[int] = 20
PAGE_BUTTON_SIZE: Final[int] = 30
PAGE_LABEL_OFFSET: Final[Vec2] = Vec2(0, -50)
TOOLTIP_TITLE_FONT_SIZE: Final[int] = 12
TOOLTIP_CONTENT_FONT_SIZE: Final[int] = 10
TOOLTIP_MAX_WIDTH: Final[int] = 300
TOOLTIP_VERTICAL_SPACING: Final[int] = 8
TOOLTIP_PADDING: Final[int] = 10
TOOLTIP_OFFSET: Final[Vec2] = Vec2(0, 10)


class InventoryUI:
    """화면 하단에 출력되는 인벤토리."""
    def __init__(
            self, 
            scene: Scene,
            layout: ItemsLayout, 
            batch: Batch,
            ui_group: Group,
            icon_size: int = 40
            ) -> None:
        self.scene: Scene = scene
        self.layout: ItemsLayout = layout
        self.batch: Batch = batch
        self.group_placeholder: Group = ui_group
        self.group_content: Group = Group(order=ui_group.order + 1, parent=ui_group)
        self.group_tooltip: Group = Group(order=ui_group.order + 5, parent=ui_group)
        self.group_tooltip_content: Group = Group(order=ui_group.order + 6, parent=self.group_tooltip)
        self.icon_size: int = icon_size
        self.pages: int = 0

        self.item_default_image = pyglet.resource.image(ITEM_DEFAULT_ICON)
        self.item_default_image.width = self.item_default_image.height = icon_size
        self.item_default_image.anchor_x = self.item_default_image.anchor_y = icon_size // 2

        self.icons: List[Sprite] = []
        self.placeholders: List[BorderedRectangle] = []
        self.index_labels: List[Label] = []

        self.items_table: Dict[int, ItemDrawData] = {}

        for i in range(layout.length):
            # self.icons.append(Sprite(self.item_blank_image, batch=batch, group=self.group_content))
            # self.icons[i].opacity = 128
            center_position: Vec2 = layout.get_position(i)
            rect_position: Vec2 = (center_position-Vec2(self.icon_size, self.icon_size)*self.scene.scale_factor/2)
            self.placeholders.append(BorderedRectangle(
                rect_position.x, rect_position.y,
                width=self.icon_size, height=self.icon_size, border=5,
                color=Color.black().tuple_256(), border_color=Color.white().tuple_256(),
                batch=batch, group=self.group_placeholder
            ))
            self.placeholders[i].opacity = 128
            self.icons.append(Sprite(
                self.item_default_image, center_position.x, center_position.y,
                batch=batch, group=self.group_content
            ))
            self.icons[i].visible = False
            self.index_labels.append(Label(
                text=str((i+1)%self.layout.length), font_name=ITEM_INDEX_FONT, font_size=ITEM_INDEX_FONT_SIZE*self.scene.scale_factor,
                color=Color.white().tuple_256(),
                x=rect_position.x + ITEM_INDEX_LABEL_OFFSET.x*self.scene.scale_factor,
                y=rect_position.y + (self.icon_size+ITEM_INDEX_LABEL_OFFSET.y)*self.scene.scale_factor,
                batch=batch, group=self.group_content
            ))

        self.tooltip_index: int = 0
        self.tooltip_bg = BorderedRectangle(
            0, 0, 100, 100, border=3,
            color=Color.black().tuple_256(), border_color=Color.white().tuple_256(),
            batch=batch, group=self.group_tooltip
        )
        self.tooltip_title = Label(
            font_name=ITEM_INDEX_FONT, font_size=TOOLTIP_TITLE_FONT_SIZE*self.scene.scale_factor,
            bold=True, color=Color.white().tuple_256(),
            batch=batch, group=self.group_tooltip_content
        )
        self.tooltip_description = Label(
            font_name=ITEM_INDEX_FONT, font_size=TOOLTIP_CONTENT_FONT_SIZE*self.scene.scale_factor,
            color=Color.white().tuple_256(),
            width=TOOLTIP_MAX_WIDTH*self.scene.scale_factor, multiline=True,
            batch=batch, group=self.group_tooltip_content
        )
        self.tooltip_additional_description = Label(
            font_name=ITEM_INDEX_FONT, font_size=TOOLTIP_CONTENT_FONT_SIZE*self.scene.scale_factor,
            color=Color.green().tuple_256(), italic=True,
            batch=batch, group=self.group_tooltip_content
        )
        self.group_tooltip.visible = False

        pagebtn_highlight_state = SolidButtonState(
            box_color=Color.white(), border_color=Color.white(),
            label_color=Color.black(), transition=0.3
        )
        pagebtn_normal_state = SolidButtonState(
            box_color=Color.black(), border_color=Color.white(),
            label_color=Color.white(), transition=0.3
        )
        pagebtn_disenabled_state = SolidButtonState(
            box_color=Color.black()*0.5, border_color=Color.white()*0.5,
            label_color=Color.white()*0.5, transition=0.3
        )
        pagebtn_option = dict(
            scene=self.scene,
            y=self.layout.y,
            width=PAGE_BUTTON_SIZE, height=PAGE_BUTTON_SIZE,
            border=3, font_family=ITEM_INDEX_FONT, font_size=PAGE_BUTTON_SIZE*0.8,
            pressed=pagebtn_highlight_state, depressed=pagebtn_normal_state,
            scale_factor=self.scene.scale_factor,
            hover=pagebtn_highlight_state, disenabled=pagebtn_disenabled_state,
            anchor=AnchorPreset.BottomLeft,
            batch=batch, group=self.group_placeholder
        )
        self.pagebtn_prev = SolidButton(
            text="<", x=self.layout.get_position(-1, scaled=False).x, **pagebtn_option
        )
        self.pagebtn_next = SolidButton(
            text=">", x=self.layout.get_position(self.layout.length, scaled=False).x, **pagebtn_option
        )
        self.pagelabel = Label(
            text="1", font_name=ITEM_INDEX_FONT, font_size=PAGE_FONT_SIZE,
            x=self.scene.window.width/2 + PAGE_LABEL_OFFSET.x*self.scene.scale_factor, 
            y=self.layout.y + PAGE_LABEL_OFFSET.y*self.scene.scale_factor,
            anchor_x="center", align="center",
            batch=batch, group=self.group_content
        )
        self.pagebtn_prev.push_handlers(on_press=self.prev_page)
        self.pagebtn_next.push_handlers(on_press=self.next_page)

        # pages가 0에서 시작하므로 이전 페이지 버튼 비활성화.
        self.pagebtn_prev.set_enabled(False)

        self.scene.push_handlers(on_scene_window_resized=lambda w,h: self.update_layout())

        def on_mouse_motion(x: int, y: int, dx: int, dy: int):
            if (index := self._calc_hovered_index(Vec2(x, y))) >= 0 \
                and (item_index := index + self.pages*self.layout.length) in self.items_table:
                self._show_tooltip(index, self.items_table[item_index])
            else:
                self._hide_tooltip()
        
        self.scene.window.push_handlers(on_mouse_motion)

        # self.scene.window.push_handlers(on_mouse_motion=lambda x,y,dx,dy: print(self._calc_hovered_index(Vec2(x,y))))

    def update_layout(self) -> None:
        self.pagebtn_prev.position = self.layout.get_position(-1, scaled=False)
        self.pagebtn_next.position = self.layout.get_position(self.layout.length, scaled=False)
        self.pagelabel.font_size = PAGE_FONT_SIZE*self.scene.scale_factor
        self.pagelabel.position = *(
            Vec2(self.scene.window.width/2, 0) 
            + (Vec2(0, self.layout.y) + PAGE_LABEL_OFFSET)*self.scene.scale_factor), 0
        for i in range(self.layout.length):
            center_position: Vec2 = self.layout.get_position(i)
            rect_position: Vec2 = (center_position-Vec2(self.icon_size, self.icon_size)*self.scene.scale_factor/2)
            self.placeholders[i].width = self.placeholders[i].height = self.icon_size * self.scene.scale_factor
            self.placeholders[i].position = (*rect_position,)
            self.icons[i].scale = ICON_CONTENT_SCALE * self.scene.scale_factor
            self.icons[i].position = (*center_position, 0)
            self.index_labels[i].font_size = ITEM_INDEX_FONT_SIZE*self.scene.scale_factor
            self.index_labels[i].position = *(rect_position + (Vec2(0, self.icon_size)+ITEM_INDEX_LABEL_OFFSET)*self.scene.scale_factor), 0

        if self.group_tooltip.visible and self._calc_hovered_index(self.tooltip_index):
            self.tooltip_title.font_size = TOOLTIP_TITLE_FONT_SIZE * self.scene.scale_factor
            self.tooltip_description.font_size = self.tooltip_additional_description.font_size = \
                TOOLTIP_CONTENT_FONT_SIZE * self.scene.scale_factor
            self.tooltip_description.width = TOOLTIP_MAX_WIDTH * self.scene.scale_factor
            self._update_tooltip_layout(self.tooltip_index)

    def update_image(self) -> None:
        for i in range(self.layout.length):
            global_index: int = i + self.layout.length*self.pages
            if global_index in self.items_table:
                item_data: ItemDrawData = self.items_table[global_index]
                try:
                    img = pyglet.resource.image(item_data.sprite_name)
                except pyglet.resource.ResourceNotFoundException:
                    img = pyglet.resource.image(ITEM_DEFAULT_ICON)
                img.width = img.height = self.icon_size
                img.anchor_x = img.anchor_y = self.icon_size // 2
                self.icons[i].image = img
                self.icons[i].visible = True
                self.placeholders[i].opacity = 255
                self.index_labels[i].opacity = 255
            else:
                self.icons[i].visible = False
                self.placeholders[i].opacity = 32
                self.index_labels[i].opacity = 64
            
    def push_item(self, item_data: ItemDrawData) -> None:
        """아이템을 목록에 추가.
        
        비어 있는 가장 작은 인덱스에 할당하며, 할당 후 해당 페이지를 보여 줌."""
        index: int = 0
        while index in self.items_table:
            index += 1
        self.items_table[index] = item_data
        self.pages = index // self.layout.length
        self.update_image()

    def remove_item(self, item_id: int) -> None:
        """아이템을 목록에서 제거."""
        for key, value in self.items_table.items():
            if value.id == item_id:
                del self.items_table[key]
                break
        self.update_image()
    
    def prev_page(self) -> None:
        """이전 페이지를 보여 줌."""
        if self.pages > 0:
            self.pages -= 1
            self.pagelabel.text = str(self.pages+1)
            if self.pages == 0:
                self.pagebtn_prev.set_enabled(False)
            self.update_image()

    def next_page(self) -> None:
        """다음 페이지를 보여 줌."""
        self.pages += 1
        self.pagelabel.text = str(self.pages+1)
        self.pagebtn_prev.set_enabled(True)
        self.update_image()

    def _calc_hovered_index(self, mouse_pos: Vec2) -> int:
        """마우스 커서 위치를 받아 현재 커서가 위치한 슬롯 인덱스 계산.
        
        커서가 아이템 슬롯 중 어디에도 없을 경우 -1 반환."""
        mouse_pos /= self.scene.scale_factor
        if abs(mouse_pos.y - self.layout.y)*2 > self.icon_size \
            or mouse_pos.x < (layout_left := self.layout.get_position(0, scaled=False).x-self.icon_size/2) \
            or mouse_pos.x > self.layout.get_position(self.layout.length-1, scaled=False).x+self.icon_size/2 \
            or (local_x := mouse_pos.x - layout_left) % self.layout.space > self.icon_size:
            return -1
        return int(local_x / self.layout.space)

    def _show_tooltip(self, index: int, data: ItemDrawData):
        """주어진 정보를 이용해 툴팁을 보임."""
        if self.group_tooltip.visible and index == self.tooltip_index:
            return
        self.tooltip_index = index
        self.tooltip_title.font_size = TOOLTIP_TITLE_FONT_SIZE * self.scene.scale_factor
        self.tooltip_description.font_size = self.tooltip_additional_description.font_size = \
            TOOLTIP_CONTENT_FONT_SIZE * self.scene.scale_factor
        self.tooltip_description.width = TOOLTIP_MAX_WIDTH * self.scene.scale_factor
        self.tooltip_title.text = data.name
        self.tooltip_description.text = data.description
        self.tooltip_additional_description.text = f"사용하려면 아이콘을 클릭하거나 '{index+1}' 키를 입력하세요."
        
        self._update_tooltip_layout(index)
        self.group_tooltip.visible = True

    def _hide_tooltip(self):
        self.group_tooltip.visible = False

    def _update_tooltip_layout(self, index: int):
        self.tooltip_bg.width = max(
            self.tooltip_title.content_width, 
            self.tooltip_description.content_width,
            self.tooltip_additional_description.content_width
        ) + TOOLTIP_PADDING * 2 * self.scene.scale_factor
        self.tooltip_bg.height = self.tooltip_title.content_height \
            + self.tooltip_description.content_height \
            + self.tooltip_additional_description.content_height \
            + (TOOLTIP_PADDING + TOOLTIP_VERTICAL_SPACING)*2*self.scene.scale_factor
        
        self.tooltip_bg.position = self.layout.get_position(index) \
            + Vec2(-self.tooltip_bg.width/2, 0) \
            + (Vec2(0, self.icon_size/2)  + TOOLTIP_OFFSET) * self.scene.scale_factor
        self.tooltip_additional_description.position = *(
            Vec2(*self.tooltip_bg.position)
            + Vec2(TOOLTIP_PADDING, TOOLTIP_PADDING) * self.scene.scale_factor
        ), 0
        self.tooltip_description.position = *(
            Vec2(*self.tooltip_additional_description.position[:2])
            + Vec2(0, TOOLTIP_VERTICAL_SPACING*self.scene.scale_factor + self.tooltip_additional_description.content_height)
        ), 0
        self.tooltip_title.position = *(
            Vec2(*self.tooltip_description.position[:2])
            + Vec2(0, TOOLTIP_VERTICAL_SPACING*self.scene.scale_factor + self.tooltip_description.content_height)
        ), 0