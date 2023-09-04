from typing import Final

from pyglet.text import Label
from pyglet.graphics import Batch, Group
from pyglet.shapes import BorderedRectangle
from gui.buttons import SolidButton

from gui.color import Color
from gui.scenes.scene import Scene


FONT_FAMILY: Final[str] = "Neo둥근모 Pro"
BOX_PADDING: Final[int] = 20
TITLE_FONT_SIZE: Final[int] = 30
CONTENT_FONT_SIZE: Final[int] = 20
CONTENT_LINE_SPACING: Final[int] = 10
BUTTON_FONT_SIZE: Final[int] = 18
BUTTON_MIN_WIDTH: Final[int] = 200


class PopupWindow:
    def __init__(
            self, 
            scene: Scene,
            border: int,
            box_color: Color,
            border_color: Color,
            button_color: Color,
            text_color: Color,
            batch: Batch,
            group: Group
            ) -> None:
        self.scene: Scene = scene
        self.batch = batch
        self.group_bg = Group(order=group.order+5, parent=group)
        self.group_content = Group(order=self.group_bg.order+1, parent=self.group_bg)
        
        self.bg = BorderedRectangle(
            0, 0, 100, 100, border=border,
            color=box_color.tuple_256(), border_color=border_color.tuple_256(),
            batch=batch, group=self.group_bg
        )
        self.label_title = Label(
            font_name=FONT_FAMILY, font_size=TITLE_FONT_SIZE, bold=True,
            color=text_color.tuple_256(), 
            anchor_x="center", anchor_y="top", align="center",
            batch=batch, group=self.group_content
        )
        self.label_content = Label(
            font_name=FONT_FAMILY, font_size=CONTENT_FONT_SIZE,
            color=text_color.tuple_256(),
            anchor_x="center", anchor_y="top", align="center",
            batch=batch, group=self.group_content
        )

        raise NotImplementedError
        self.submit_btn = SolidButton(
            scene=self.scene, x=0, y=0, width=100, height=100, border=border,
            text="확인", font_size=BUTTON_FONT_SIZE
        )