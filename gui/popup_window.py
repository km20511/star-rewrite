from typing import Any, Callable, Final

from pyglet.text import Label
from pyglet.graphics import Batch, Group
from pyglet.shapes import BorderedRectangle

from gui.color import Color
from gui.scenes.scene import Scene
from gui.anchored_widget import AnchorPreset
from gui.buttons import SolidButton, SolidButtonState


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
            button_bg_color: Color,
            button_content_color: Color,
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

        self.submit_btn = SolidButton(
            scene=self.scene, x=0, y=0, width=100, height=100, border=border,
            text="확인", font_family=FONT_FAMILY, font_size=BUTTON_FONT_SIZE,
            pressed=(btn_highlight:=SolidButtonState(
                box_color=button_content_color, border_color=button_content_color,
                label_color=button_bg_color, transition=0.3
            )),
            depressed=SolidButtonState(
                box_color=button_bg_color, border_color=button_content_color,
                label_color=button_content_color, transition=0.3
            ),
            hover=btn_highlight,
            anchor=AnchorPreset.BottomCenter, pivot=AnchorPreset.TopCenter,
            scale_factor=self.scene.scale_factor,
            batch=batch, group=self.group_content
        )
        
        self.hide()

    def show_popup(self, title: str, content: str, submit_msg: str, on_submit: Callable[[], Any]):
        """주어진 메시지를 담은 popup을 출력."""
        self.label_title.text = title
        self.label_content.text = content
        self.submit_btn._label.text = submit_msg
        self.submit_btn.on_press = on_submit

        raise NotImplementedError
        self.submit_btn.set_base_size()

    def hide(self):
        self.group_bg.visible = False
        self.submit_btn.enabled = False