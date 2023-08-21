"""게임 진행 중 생기는 이벤트를 호출하고 관리하는 스크립트."""
from types import CodeType
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

from core.card import Card
from core.item import Item
from core.enums import EffectTarget, EventType, PlayerStat
from core.event_handlers import (
    EventHandlerBase,
    EventHandler0,
    EventHandler1,
    EventHandler3,
    EventHandlerList,
    EventHandlerType_co,
)
from core.obj_data_formats import DrawEvent, EffectData

if TYPE_CHECKING:
    from core.effect import Effect
    from core.game_manager import GameManager


class EventManager:
    """게임 내 이벤트를 호출하는 관리자."""

    def __init__(self, game_manager: "GameManager") -> None:
        self.__game_manager: "GameManager" = game_manager
        self.__on_card_shown_listeners: List[EventHandler1[Card]] = []
        self.__on_card_entered_listeners: List[EventHandler1[Card]] = []
        self.__on_card_purchased_listeners: List[EventHandler1[Card]] = []
        self.__on_item_used_listeners: List[EventHandler1[Item]] = []
        self.__on_card_created_listeners: List[EventHandler1[Card]] = []
        self.__on_card_destroyed_listeners: List[EventHandler1[Card]] = []
        self.__on_item_created_listeners: List[EventHandler1[Item]] = []
        self.__on_item_destroyed_listeners: List[EventHandler1[Item]] = []
        self.__on_player_stat_changed_listeners: List[
            EventHandler3[PlayerStat, int, int]
        ] = []
        self.__on_turn_begin_listeners: List[EventHandler1[int]] = []
        self.__on_turn_end_listeners: List[EventHandler1[int]] = []
        self.__on_card_cost_changed_listeners: List[EventHandler3[Card, int, int]] = []
        self.__on_card_moved_listeners: List[EventHandler3[Card, int, int]] = []
        self.__on_calculate_card_cost: List[EventHandler0] = []

        self.__listeners_table: Dict[EventType, EventHandlerList[EventHandlerType_co]] = {
            EventType.OnShown: self.__on_card_shown_listeners,
            EventType.OnEntered: self.__on_card_entered_listeners,
            EventType.OnPurchased: self.__on_card_purchased_listeners,
            EventType.OnUsed: self.__on_item_used_listeners,
            EventType.OnCardCreated: self.__on_card_created_listeners,
            EventType.OnCardDestroyed: self.__on_card_destroyed_listeners,
            EventType.OnItemCreated: self.__on_item_created_listeners,
            EventType.OnItemDestroyed: self.__on_item_destroyed_listeners,
            EventType.OnPlayerStatChanged: self.__on_player_stat_changed_listeners,
            EventType.OnTurnBegin: self.__on_turn_begin_listeners,
            EventType.OnTurnEnd: self.__on_turn_end_listeners,
            EventType.OnCardCostChanged: self.__on_card_cost_changed_listeners,
            EventType.OnCardMoved: self.__on_card_moved_listeners,
            EventType.OnCalculateCardCost: self.__on_calculate_card_cost,
        }

        self.__event_queue: List[Callable[[], None]] = []
        self.__draw_event_queue: List[DrawEvent] = []

    def _compile_and_check(self, code: str) -> Optional[CodeType]:
        """해당 문자열을 compile하고 조건을 만족하는지 검사.
        문제 없이 해석된 경우: code 객체 반환
        빈문자열인 경우: None 반환
        오류가 생긴 경우: 해당 오류 그대로 발생
        금지어(예: __class__)를 포함하는 경우: NameError 발생
        """
        if code.strip() == "":
            return None
        result = compile(code, "<string>", "eval")
        disallowed_table = ("__class__",)
        for disallowed in disallowed_table:
            if disallowed in result.co_names:
                raise NameError(
                    f"스크립트 파싱 중 오류: `{code}`\n`{disallowed}`의 사용은 허용되지 않습니다."
                )
        return result

    def register_effect(self, effect_obj: "Effect"):
        """주어진 효과 객체를 이벤트 목록에 등록.
        주의: 스크립트 해석 시 발생하는 오류가 그대로 발생함."""
        effect_data: EffectData = effect_obj.data
        # 스크립트 컴파일
        effect = self._compile_and_check(effect_data.effect)
        if effect is None:
            print(f"요류: effect 필드가 비어 있음.")
            return
        query = self._compile_and_check(effect_data.query)
        order_method = self._compile_and_check(effect_data.order_method)
        order_crop = self._compile_and_check(effect_data.order_crop)
        args = {k: self._compile_and_check(v) for k, v in effect_data.args.items()}

        # 이벤트 발생 시마다 호출될 함수.
        def inner_func(game_manager: "GameManager", **kwargs):
            # 코드 단축용 함수.
            def eval_readonly_script(script, this):
                temp_table = readonlys | kwargs
                if this is not None:
                    temp_table |= {"this": this}
                return eval(
                    script,
                    # 내장 함수를 사용하지 못하게 함.
                    {"__builtins__": {}},
                    # 사용 가능한 변수/함수 한정.
                    (
                        temp_table
                        | {
                            k: eval(v, {"__builtins__": {}}, temp_table)
                            for k, v in args.items()
                            if v is not None
                        }
                    ),
                )

        # 게임에 영향을 주지 않고 정보만 얻을 수 있는 참조.
            readonlys: Dict[str, Any] = (
                self.__game_manager.get_readable_static_table()
                | self.__game_manager.deck.get_readable_static_table()
                | self.__game_manager.inventory.get_readable_static_table()
                | {"executer": effect_obj.owner}
            )
            # 덱의 카드를 대상으로 하는 효과의 경우
            if effect_data.target == EffectTarget.Deck or (
                effect_data.target != EffectTarget.Inventory
                and isinstance(effect_obj.owner, Card)
            ):
                deck_query = game_manager.deck.create_query()

                if query is not None:
                    deck_query.set_query(
                        lambda card: ((
                            # 대상이 실행 주체로 한정된 경우 이를 검사하는 조건 추가.
                            card == effect_obj.owner
                            if effect_data.target == EffectTarget.Executer
                            else True
                        )
                        and eval_readonly_script(query, card))
                    )
                elif effect_data.target == EffectTarget.Executer:
                    # query가 주어지지 않더라도 Executer의 조건 추가.
                    deck_query.set_query(lambda card: card == effect_obj.owner)

                if order_method is not None and order_crop is not None:
                    deck_query.set_order(
                        lambda card: eval_readonly_script(order_method, card),
                        eval(order_crop, {"__builtins__": {}}, readonlys | kwargs)
                    )
                    
                writables = (
                    game_manager.get_writable_static_table() 
                    | game_manager.deck.get_writable_static_table(deck_query)
                )
            
            # 인벤토리의 아이템을 대상으로 하는 효과의 경우
            elif effect_data.target == EffectTarget.Inventory or isinstance(effect_obj.owner, Item):
                inven_query = game_manager.inventory.create_query()

                if query is not None:
                    inven_query.set_query(
                        lambda item: ((
                            item == effect_obj.owner
                            if effect_data.target == EffectTarget.Executer
                            else True
                        )
                        and eval_readonly_script(query, item))
                    )
                elif effect_data.target == EffectTarget.Executer:
                    inven_query.set_query(lambda item: item == effect_obj.owner)

                if order_method is not None and order_crop is not None:
                    inven_query.set_order(
                        lambda item: eval_readonly_script(order_method, item),
                        eval(order_crop, {"__builtins__": {}}, readonlys | kwargs)
                    )

                writables = (
                    game_manager.get_writable_static_table()
                    | game_manager.inventory.get_writable_static_table(inven_query)
                )

            # EffectTarget이 Executer이고 실행 주체가 Card도 Item도 아닌 경우
            else:
                writables = (
                    game_manager.get_writable_static_table()
                )

            eval(effect, {"__builtins__": {}}, (
                readonlys | writables | kwargs | {
                    k: eval(v, {"__builtins__": {}}, readonlys | kwargs)
                    for k, v in args.items()
                    if v is not None
                }
            ))

            self.invoke_events(recursive=True)

        # 이게 맞나...?
        match (effect_data.event_type):
            case EventType.OnShown | EventType.OnEntered | EventType.OnPurchased | EventType.OnCardCreated | EventType.OnCardDestroyed:
                self.__listeners_table[effect_data.event_type].append(EventHandler1[Card](
                    effect_obj,
                    lambda gm, card: inner_func(gm, target=card)
                ))
            case EventType.OnUsed | EventType.OnItemCreated | EventType.OnItemDestroyed:
                self.__listeners_table[effect_data.event_type].append(EventHandler1[Item](
                    effect_obj,
                    lambda gm, card: inner_func(gm, target=card)
                ))
            case EventType.OnPlayerStatChanged:
                self.__on_player_stat_changed_listeners.append(EventHandler3[PlayerStat, int, int](
                    effect_obj,
                    lambda gm, stat_type, previous, current: inner_func(gm, player_stat_type=stat_type, previous=previous, current=current)
                ))
            case EventType.OnTurnBegin | EventType.OnTurnEnd:
                self.__listeners_table[effect_data.event_type].append(EventHandler1[int](
                    effect_obj,
                    lambda gm, cur_turn: inner_func(gm, current_turn=cur_turn)
                ))
            case EventType.OnCardCostChanged | EventType.OnCardMoved:
                self.__listeners_table[effect_data.event_type].append(EventHandler3[Card, int, int](
                    effect_obj,
                    lambda gm, card, previous, current: inner_func(gm, target=card, previous=previous, current=current)
                ))
            case EventType.OnCalculateCardCost:
                self.__on_calculate_card_cost.append(EventHandler0(
                    effect_obj,
                    lambda gm: inner_func(gm)
                ))

    def unregister_effect(self, effect: "Effect"):
        """주어진 효과 객체가 여기 등록되어 있다면 등록 해제."""
        target = tuple(filter(lambda x: x.owner == effect, self.__listeners_table[effect.data.event_type]))
        if len(target) > 0:
            self.__listeners_table[effect.data.event_type].remove(target[0])

    def add_listener(self, listener: EventHandlerBase, type: EventType):
        """이벤트 구독자를 추가. (주의: listener와 type 간 유형 불일치를 감지하지 못 함.)"""
        if listener not in self.__listeners_table[type]:
            self.__listeners_table[type].append(listener)

    def remove_listener(self, listener: EventHandlerBase, type: EventType):
        """해당 이벤트 구독자 등록 해제.(주의: listener와 type 간 유형 불일치를 감지하지 못 함.)"""
        if listener in self.__listeners_table[type]:
            self.__listeners_table[type].remove(listener)

    def clear_listeners(self, type: EventType):
        """이벤트 구독자 목록 초기화."""
        self.__listeners_table[type].clear()

    def push_draw_event(self, draw_state: DrawEvent):
        """DrawEvent를 큐에 추가."""
        print(f"Debug: DrawEvent Pushed {draw_state}")
        self.__draw_event_queue.append(draw_state)

    def get_draw_event(self) -> List[DrawEvent]:
        """DrawEvent 큐의 모든 이벤트를 제거하고 반환."""
        copied_queue: List[DrawEvent] = self.__draw_event_queue.copy()
        self.__draw_event_queue.clear()
        return copied_queue

    def on_card_shown(
        self, target: Card, immediate: bool = False
    ):
        """카드가 공개되었을 때 이벤트 발생. immediate가 False인 경우 바로 실행하지 않고 이벤트 큐에 등록한다."""
        if immediate:
            for listener in self.__on_card_shown_listeners:
                listener.invoke(self.__game_manager, target)
        else:
            for listener in self.__on_card_shown_listeners:
                self.__event_queue.append(lambda: listener.invoke(self.__game_manager, target))

    def on_card_entered(
        self, target: Card, immediate: bool = False
    ):
        """카드가 조작 가능 범위에 진입했을 때 이벤트 발생. immediate가 False인 경우 바로 실행하지 않고 이벤트 큐에 등록한다."""
        if immediate:
            for listener in self.__on_card_entered_listeners:
                listener.invoke(self.__game_manager, target)
        else:
            for listener in self.__on_card_entered_listeners:
                self.__event_queue.append(lambda: listener.invoke(self.__game_manager, target))

    def on_card_purchased(
        self, target: Card, immediate: bool = False
    ):
        """플레이어가 덱에서 카드를 구매하거나 적을 처치했을 때 이벤트 발생. immediate가 False인 경우 바로 실행하지 않고 이벤트 큐에 등록한다."""
        if immediate:
            for listener in self.__on_card_purchased_listeners:
                listener.invoke(self.__game_manager, target)
        else:
            for listener in self.__on_card_purchased_listeners:
                self.__event_queue.append(lambda: listener.invoke(self.__game_manager, target))

    def on_item_used(
        self, target: Item, immediate: bool = False
    ):
        """플레이어가 인벤토리에서 아이템을 사용했을 때 이벤트 발생. immediate가 False인 경우 바로 실행하지 않고 이벤트 큐에 등록한다."""
        if immediate:
            for listener in self.__on_item_used_listeners:
                listener.invoke(self.__game_manager, target)
        else:
            for listener in self.__on_item_used_listeners:
                self.__event_queue.append(lambda: listener.invoke(self.__game_manager, target))

    def on_card_created(
        self, target: Card, immediate: bool = False
    ):
        """덱에서 카드가 생성되었을 때 이벤트 발생. immediate가 False인 경우 바로 실행하지 않고 이벤트 큐에 등록한다."""
        if immediate:
            for listener in self.__on_card_created_listeners:
                listener.invoke(self.__game_manager, target)
        else:
            for listener in self.__on_card_created_listeners:
                self.__event_queue.append(lambda: listener.invoke(self.__game_manager, target))

    def on_card_destroyed(
        self, target: Card, immediate: bool = False
    ):
        """덱에서 카드가 파괴되었을 때 이벤트 발생. immediate가 False인 경우 바로 실행하지 않고 이벤트 큐에 등록한다."""
        if immediate:
            for listener in self.__on_card_destroyed_listeners:
                listener.invoke(self.__game_manager, target)
        else:
            for listener in self.__on_card_destroyed_listeners:
                self.__event_queue.append(lambda: listener.invoke(self.__game_manager, target))

    def on_item_created(
        self, target: Item, immediate: bool = False
    ):
        """인벤토리에서 아이템이 생성되었을 때 이벤트 발생. immediate가 False인 경우 바로 실행하지 않고 이벤트 큐에 등록한다."""
        if immediate:
            for listener in self.__on_item_created_listeners:
                listener.invoke(self.__game_manager, target)
        else:
            for listener in self.__on_item_created_listeners:
                self.__event_queue.append(lambda: listener.invoke(self.__game_manager, target))

    def on_item_destroyed(
        self, target: Item, immediate: bool = False
    ):
        """인벤토리에서 아이템이 파괴되었을 때 이벤트 발생. immediate가 False인 경우 바로 실행하지 않고 이벤트 큐에 등록한다."""
        if immediate:
            for listener in self.__on_item_destroyed_listeners:
                listener.invoke(self.__game_manager, target)
        else:
            for listener in self.__on_item_destroyed_listeners:
                self.__event_queue.append(lambda: listener.invoke(self.__game_manager, target))

    def on_player_stat_changed(
        self,
        stat_type: PlayerStat,
        previous: int,
        current: int,
        immediate: bool = False,
    ):
        """체력 등 플레이어의 능력치에 변동이 생겼을 때 이벤트 발생. immediate가 False인 경우 바로 실행하지 않고 이벤트 큐에 등록한다."""
        if immediate:
            for listener in self.__on_player_stat_changed_listeners:
                listener.invoke(self.__game_manager, stat_type, previous, current)
        else:
            for listener in self.__on_player_stat_changed_listeners:
                self.__event_queue.append(
                    lambda: listener.invoke(self.__game_manager, stat_type, previous, current)
                )

    def on_turn_begin(
        self, current_turn: int, immediate: bool = False
    ):
        """턴이 시작했을 때 이벤트 발생. immediate가 False인 경우 바로 실행하지 않고 이벤트 큐에 등록한다."""
        if immediate:
            for listener in self.__on_turn_begin_listeners:
                listener.invoke(self.__game_manager, current_turn)
        else:
            for listener in self.__on_turn_begin_listeners:
                self.__event_queue.append(
                    lambda: listener.invoke(self.__game_manager, current_turn)
                )

    def on_turn_end(
        self, current_turn: int, immediate: bool = False
    ):
        """턴이 끝날 때 이벤트 발생. immediate가 False인 경우 바로 실행하지 않고 이벤트 큐에 등록한다."""
        if immediate:
            for listener in self.__on_turn_end_listeners:
                listener.invoke(self.__game_manager, current_turn)
        else:
            for listener in self.__on_turn_end_listeners:
                self.__event_queue.append(
                    lambda: listener.invoke(self.__game_manager, current_turn)
                )

    def on_card_cost_changed(
        self,
        target: Card,
        previous: int,
        current: int,
        immediate: bool = False,
    ):
        """카드의 비용(적의 경우 체력)이 변동되었을 때 이벤트 발생. immediate가 False인 경우 바로 실행하지 않고 이벤트 큐에 등록한다."""
        if immediate:
            for listener in self.__on_card_cost_changed_listeners:
                listener.invoke(self.__game_manager, target, previous, current)
        else:
            for listener in self.__on_card_cost_changed_listeners:
                self.__event_queue.append(
                    lambda: listener.invoke(self.__game_manager, target, previous, current)
                )

    def on_card_moved(
        self,
        target: Card,
        previous: int,
        current: int,
        immediate: bool = False,
    ):
        """카드가 이동했을 때 이벤트 발생. immediate가 False인 경우 바로 실행하지 않고 이벤트 큐에 등록한다."""
        if immediate:
            for listener in self.__on_card_moved_listeners:
                listener.invoke(self.__game_manager, target, previous, current)
        else:
            for listener in self.__on_card_moved_listeners:
                self.__event_queue.append(
                    lambda: listener.invoke(self.__game_manager, target, previous, current)
                )

    def on_calculate_card_cost(
        self, immediate: bool = False
    ):
        if immediate:
            for listener in self.__on_calculate_card_cost:
                listener.invoke(self.__game_manager)
        else:
            for listener in self.__on_calculate_card_cost:
                self.__event_queue.append(lambda: listener.invoke(self.__game_manager))

    def invoke_events(self, recursive: bool = False):
        """이벤트 큐의 모든 이벤트 실행."""
        executing_events = self.__event_queue.copy()
        self.__event_queue.clear()
        while len(executing_events) > 0:
            executing_events.pop(0)()
        
        if recursive and len(self.__event_queue) > 0:
            self.invoke_events(recursive)
