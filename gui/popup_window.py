from typing import Any, Callable, Final

from pyglet.math import Vec2
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
CONTENT_LINE_SPACING: Final[int] = 20
CONTENT_MAX_WIDTH: Final[int] = 600
BUTTON_SIZE: Final[Vec2] = Vec2(200, 60)
BUTTON_FONT_SIZE: Final[int] = 18


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
        self.group_bg = Group(order=group.order+10, parent=group)
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
            color=text_color.tuple_256(), multiline=True, width=CONTENT_MAX_WIDTH,
            anchor_x="center", anchor_y="top", align="center",
            batch=batch, group=self.group_content
        )

        self.submit_btn = SolidButton(
            scene=self.scene, x=0, y=0, width=BUTTON_SIZE.x, height=BUTTON_SIZE.y, border=border,
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

        def on_resize(w, h):
            self.update_layout()

        self.scene.push_handlers(on_scene_window_resized=on_resize)

        # self.hide()

    @property
    def enabled(self) -> bool:
        return self.group_bg.visible

    def show_popup(self, title: str, content: str, submit_msg: str, on_submit: Callable[[], Any]):
        """주어진 메시지를 담은 popup을 출력."""

        self.group_bg.visible = True
        
        self.label_title.text = title
        self.label_content.text = content
        self.submit_btn._label.text = submit_msg

        def on_press():
            self.hide()
            on_submit()

        self.submit_btn.on_press = on_press
        self.submit_btn.set_enabled(True)

        self.update_layout()

    def update_layout(self):
        if not self.group_bg.visible:
            return
        
        self.label_title.font_size = TITLE_FONT_SIZE * self.scene.scale_factor
        self.label_content.font_size = CONTENT_FONT_SIZE * self.scene.scale_factor

        self.bg.width = max(
            self.label_title.content_width, self.label_content.content_width,
            self.submit_btn.width) + BOX_PADDING*2*self.scene.scale_factor
        self.bg.height = self.label_title.content_height \
            + self.label_content.content_height \
            + self.submit_btn.height + BOX_PADDING*2*self.scene.scale_factor \
            + CONTENT_LINE_SPACING*2*self.scene.scale_factor
        # self.bg.anchor_position = self.bg.width // 2, self.bg.height // 2
        self.bg.position = (self.scene.window.width - self.bg.width) // 2, (self.scene.window.height - self.bg.height) // 2

        bg_top = (self.scene.window.height + self.bg.height) // 2

        self.label_title.position = (self.scene.window.width // 2, bg_top - BOX_PADDING * self.scene.scale_factor, 0)
        self.label_content.position = (
            self.scene.window.width // 2, self.label_title.y \
            - self.label_title.content_height \
            - CONTENT_LINE_SPACING * self.scene.scale_factor, 0
        )
        self.submit_btn.set_base_position(Vec2(
            0, (self.label_content.y - self.label_content.content_height) / self.scene.scale_factor \
            - CONTENT_LINE_SPACING
        ))

    def hide(self):
        self.group_bg.visible = False
        self.submit_btn.enabled = False

    def delete(self):
        self.bg.delete()
        self.label_title.delete()
        self.label_content.delete()
        self.submit_btn.delete()