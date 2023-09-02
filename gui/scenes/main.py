from typing import Any, Dict, Final, List, Optional, Tuple

import pyglet
from pyglet.math import Vec2

from core import GameManager
from core.enums import CardType, DrawEventType, PlayerStat
from core.obj_data_formats import DrawEvent, ItemDrawData
from gui.anchored_widget import AnchorPreset
from gui.buttons import SolidButton, SolidButtonState
from gui.card import Card
from gui.color import Color
from gui.elements_layout import CardsLayout, ItemsLayout
from gui.inventory_ui import InventoryUI
from gui.player_hud import HUDValueType, PlayerHUD
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
            self.frame_display.draw()

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
            scroll_sensitivity=15.0
        )

        self.cards = [Card(data, self.card_layout, self.card_batch, self.card_group, self.card_thumnail_group, self.card_text_group, index=index)
                    for index, data in enumerate(self.game_state.deck)]

        self.buy_button = SolidButton(
            self, x=0, y=130, width=200, height=50, border=3, 
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

        self.item_layout = ItemsLayout(self, 10, space=60, y=60, height=50)
        self.inventory = InventoryUI(
            self, 
            layout=self.item_layout, 
            batch=self.ui_batch,
            ui_group=self.ui_group,
            icon_size=50)
        self.inventory.push_item(ItemDrawData(1234, "입문자의 목검", "item_wooden_sword.png", "사용 시: 이번 턴에만 공격력을 2 얻습니다."))
        self.inventory.push_item(ItemDrawData(2382, "아르바이트 수행", "item_parttime_job.png", "사용 시: 3골드를 얻습니다."))

        self.card_layout.push_handlers(on_selection_changed=lambda index: self.buy_button.set_enabled(self._check_purchasable(index)))
        self.buy_button.set_enabled(self._check_purchasable(0))

    def _check_purchasable(self, index: int) -> bool:
        """카드가 구매 가능한지 확인."""
        if not (0 <= index < len(self.game_state.deck) or self.user_controllable):
            return False
        card = self.game_state.deck[index]
        if not card.is_front_face or self.game_state.player_remaining_action <= 0:
            return False
        return (self.game_state.player_health + self.game_state.player_attack >= card.current_cost
                if card.type == CardType.Enemy
                else self.game_state.player_money >= card.current_cost)
    
    def _remove_card(self, card: Card):
        card.delete()
        self.cards.remove(card)

    def _rearrange_card(self, changes: List[Tuple[Card, int]]):
        """주어진 카드 이동 정보를 이용해 self.cards를 재배치.
        
        도중에 전체 길이의 변화나 위치 충돌 등이 없다고 전제함."""
        raise NotImplementedError

    def _pop_same_drawevents(self, drawevents: List[DrawEvent | Any], target: DrawEventType) -> List[DrawEvent]:
        """같은 종류의 연속된 DrawEvent를 전부 뽑아 옴."""
        result: List[DrawEvent] = []
        while len(drawevents) > 0 and isinstance(drawevents[0], DrawEvent) and drawevents[0].event_type == target:
            result.append(drawevents.pop(0))
        return result
    
    def process_draw_events(self) -> None:
        """현재까지 발생한 DrawEvent를 순서대로 처리."""
        draw_events = self.game.get_draw_events()
        self.set_user_controllable(False)
        invoke_after: float = 0.0
        while len(draw_events) > 0:
            event = draw_events.pop(0)
            if isinstance(event, DrawEvent):
                match (event.event_type):
                    case DrawEventType.TurnBegin:
                        pyglet.clock.schedule_once(self.hud.set_states, invoke_after, states={HUDValueType.Turn: (event.current, True)}, duration=2.0)
                        invoke_after += 2.0
                    case DrawEventType.TurnEnd:
                        pass
                    case DrawEventType.CardShown:
                        # 연속된 CardShown 이벤트를 일괄 처리.
                        for i in event, *self._pop_same_drawevents(draw_events, DrawEventType.CardShown):
                            if (card := self.find_card_by_id(i.target_id)) is not None:
                                pyglet.clock.schedule_once(card.set_front_face, invoke_after, is_front_face=bool(i.current))
                        invoke_after += 0.3 # 0.3초 지연.
                    case DrawEventType.CardMoved:
                        moved_table: List[Tuple[Card, int]] = []
                        for i in event, *self._pop_same_drawevents(draw_events, DrawEventType.CardMoved):
                            if (card := self.find_card_by_id(i.target_id)) is not None:
                                pyglet.clock.schedule_once(card.move_to, invoke_after, new_index=i.current, duration=0.5)
                                moved_table.append((card, i.current))
                        self._rearrange_card(changes=moved_table)
                        invoke_after += 0.5
                    case DrawEventType.CardPurchased:
                        pass
                    case DrawEventType.CardDestroyed:
                        for i in event, *self._pop_same_drawevents(draw_events, DrawEventType.CardDestroyed):
                            if (card := self.find_card_by_id(i.target_id)) is not None:
                                pyglet.clock.schedule_once(self._remove_card, invoke_after, card=card)
                        invoke_after += 0.5
                    case DrawEventType.CardCostChanged:
                        for i in event, *self._pop_same_drawevents(draw_events, DrawEventType.CardCostChanged):
                            if (card := self.find_card_by_id(i.target_id)) is not None:
                                pyglet.clock.schedule_once(card.set_cost, invoke_after, new_cost=i.current)
                        invoke_after += 0.5
                    case DrawEventType.ItemUsed:
                        pass
                    case DrawEventType.ItemDestroyed:
                        raise NotImplementedError
                    case DrawEventType.PlayerWon:
                        raise NotImplementedError
                    case DrawEventType.PlayerLost:
                        raise NotImplementedError
                    case DrawEventType.PlayerStatChanged:
                        changed_table: Dict[HUDValueType, Tuple[int, bool]] = {}
                        key_table: Dict[PlayerStat, HUDValueType] = {
                                PlayerStat.Action: HUDValueType.Action,
                                PlayerStat.Attack: HUDValueType.Attack,
                                PlayerStat.Health: HUDValueType.Health,
                                PlayerStat.Money: HUDValueType.Money
                            }
                        for i in event, *self._pop_same_drawevents(draw_events, DrawEventType.PlayerStatChanged):
                            changed_table[key_table[PlayerStat(event.target_id)]] = (i.current, True)
                        pyglet.clock.schedule_once(self.hud.set_states, invoke_after, states=changed_table, duration=2.0)
                        invoke_after += 2.0

            elif isinstance(event, ItemDrawData):
                # 아이템 생성 이벤트.
                raise NotImplementedError
            else:
                # 카드 생성 이벤트.
                while True:
                    card = Card(event[0], self.card_layout, self.card_batch, self.card_group, self.card_thumnail_group, self.card_text_group)
        pyglet.clock.schedule_once(self.set_user_controllable, invoke_after, controllable=True)

    def find_card_by_id(self, id: int) -> Optional[Card]:
        """주어진 id를 가진 Card를 탐색."""
        for card in self.cards:
            if card.data.id == id:
                return card
        return None
            
    def set_user_controllable(self, controllable: bool) -> None:
        """(애니메이션 재생 등의 목적으로) 사용자의 입력을 받을지 설정함."""
        super().set_user_controllable(controllable)
        raise NotImplementedError
