"""게임 진행 중 생기는 이벤트를 호출하고 관리하는 스크립트."""
from typing import Callable, Dict, List

from core.card import Card
from core.game_manager import GameManager
from core.item import Item
from core.enums import EventType
from core.event_handlers import EventHandler0, EventHandlerBase, EventHandler1, EventHandler3, PlayerStat


class EventManager:
    """게임 내 이벤트를 호출하는 관리자."""
    def __init__(self) -> None:
        self.__on_card_shown_listeners: List[EventHandler1[Card]] = []
        self.__on_card_entered_listeners: List[EventHandler1[Card]] = []
        self.__on_card_purchased_listeners: List[EventHandler1[Card]] = []
        self.__on_item_used_listeners: List[EventHandler1[Item]] = []
        self.__on_card_destroyed_listeners: List[EventHandler1[Card]] = []
        self.__on_player_stat_changed_listeners: List[EventHandler3[PlayerStat, int, int]] = []
        self.__on_turn_begin_listeners: List[EventHandler1[int]] = []
        self.__on_turn_end_listeners: List[EventHandler1[int]] = []
        self.__on_card_cost_changed_listeners: List[EventHandler3[Card, int, int]] = []
        self.__on_card_moved_listeners: List[EventHandler3[Card, int, int]] = []
        self.__on_calculate_card_cost: List[EventHandler0] = []
        
        self.__listeners_table: Dict[EventType, List[EventHandlerBase]] = {
            EventType.OnShown: self.__on_card_shown_listeners,
            EventType.OnEntered: self.__on_card_entered_listeners,
            EventType.OnPurchased: self.__on_card_purchased_listeners,
            EventType.OnUsed: self.__on_item_used_listeners,
            EventType.OnDestroyed: self.__on_card_destroyed_listeners,
            EventType.OnPlayerStatChanged: self.__on_player_stat_changed_listeners,
            EventType.OnTurnBegin: self.__on_turn_begin_listeners,
            EventType.OnTurnEnd: self.__on_turn_end_listeners,
            EventType.OnCardCostChanged: self.__on_card_cost_changed_listeners,
            EventType.OnCardMoved: self.__on_card_moved_listeners,
            EventType.OnCalculateCardCost: self.__on_calculate_card_cost
        }

        self.__event_queue: List[Callable[[], None]] = []

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

    def on_card_shown(self, game_manager: GameManager, target: Card, immediate: bool = False):
        """카드가 공개되었을 때 이벤트 발생. immediate가 False인 경우 바로 실행하지 않고 이벤트 큐에 등록한다."""
        if immediate:
            for listener in self.__on_card_shown_listeners:
                listener.invoke(game_manager, target)
        else:
            for listener in self.__on_card_shown_listeners:
                self.__event_queue.append(lambda : listener.invoke(game_manager, target))

    def on_card_entered(self, game_manager: GameManager, target: Card, immediate: bool = False):
        """카드가 조작 가능 범위에 진입했을 때 이벤트 발생. immediate가 False인 경우 바로 실행하지 않고 이벤트 큐에 등록한다."""
        if immediate:
            for listener in self.__on_card_entered_listeners:
                listener.invoke(game_manager, target)
        else:
            for listener in self.__on_card_entered_listeners:
                self.__event_queue.append(lambda : listener.invoke(game_manager, target))

    def on_card_purchased(self, game_manager: GameManager, target: Card, immediate: bool = False):
        """플레이어가 덱에서 카드를 구매하거나 적을 처치했을 때 이벤트 발생. immediate가 False인 경우 바로 실행하지 않고 이벤트 큐에 등록한다."""
        if immediate:
            for listener in self.__on_card_purchased_listeners:
                listener.invoke(game_manager, target)
        else:
            for listener in self.__on_card_purchased_listeners:
                self.__event_queue.append(lambda : listener.invoke(game_manager, target))
    
    def on_item_used(self, game_manager: GameManager, target: Item, immediate: bool = False):
        """플레이어가 인벤토리에서 아이템을 사용했을 때 이벤트 발생. immediate가 False인 경우 바로 실행하지 않고 이벤트 큐에 등록한다."""
        if immediate:
            for listener in self.__on_item_used_listeners:
                listener.invoke(game_manager, target)
        else:
            for listener in self.__on_item_used_listeners:
                self.__event_queue.append(lambda : listener.invoke(game_manager, target))

    def on_card_destroyed(self, game_manager: GameManager, target: Card, immediate: bool = False):
        """덱에서 카드가 파괴되었을 때 이벤트 발생. immediate가 False인 경우 바로 실행하지 않고 이벤트 큐에 등록한다."""
        if immediate:
            for listener in self.__on_card_destroyed_listeners:
                listener.invoke(game_manager, target)
        else:
            for listener in self.__on_card_destroyed_listeners:
                self.__event_queue.append(lambda : listener.invoke(game_manager, target))
    
    def on_player_stat_changed(self, game_manager: GameManager, stat_type: PlayerStat, previous: int, current: int, immediate: bool = False):
        """체력 등 플레이어의 능력치에 변동이 생겼을 때 이벤트 발생. immediate가 False인 경우 바로 실행하지 않고 이벤트 큐에 등록한다."""
        if immediate:
            for listener in self.__on_player_stat_changed_listeners:
                listener.invoke(game_manager, stat_type, previous, current)
        else:
            for listener in self.__on_player_stat_changed_listeners:
                self.__event_queue.append(lambda : listener.invoke(game_manager, stat_type, previous, current))

    def on_turn_begin(self, game_manager: GameManager, current_turn: int, immediate: bool = False):
        """턴이 시작했을 때 이벤트 발생. immediate가 False인 경우 바로 실행하지 않고 이벤트 큐에 등록한다."""
        if immediate:
            for listener in self.__on_turn_begin_listeners:
                listener.invoke(game_manager, current_turn)
        else:
            for listener in self.__on_turn_begin_listeners:
                self.__event_queue.append(lambda : listener.invoke(game_manager, current_turn))

    def on_turn_end(self, game_manager: GameManager, current_turn: int, immediate: bool = False):
        """턴이 끝날 때 이벤트 발생. immediate가 False인 경우 바로 실행하지 않고 이벤트 큐에 등록한다."""
        if immediate:
            for listener in self.__on_turn_end_listeners:
                listener.invoke(game_manager, current_turn)
        else:
            for listener in self.__on_turn_end_listeners:
                self.__event_queue.append(lambda : listener.invoke(game_manager, current_turn))

    def on_card_cost_changed(self, game_manager: GameManager, target: Card, previous: int, current: int, immediate: bool = False):
        """카드의 비용(적의 경우 체력)이 변동되었을 때 이벤트 발생. immediate가 False인 경우 바로 실행하지 않고 이벤트 큐에 등록한다."""
        if immediate:
            for listener in self.__on_card_cost_changed_listeners:
                listener.invoke(game_manager, target, previous, current)
        else:
            for listener in self.__on_card_cost_changed_listeners:
                self.__event_queue.append(lambda : listener.invoke(game_manager, target, previous, current))

    def on_card_moved(self, game_manager: GameManager, target: Card, previous: int, current: int, immediate: bool = False):
        """카드가 이동했을 때 이벤트 발생. immediate가 False인 경우 바로 실행하지 않고 이벤트 큐에 등록한다."""
        if immediate:
            for listener in self.__on_card_moved_listeners:
                listener.invoke(game_manager, target, previous, current)
        else:
            for listener in self.__on_card_moved_listeners:
                self.__event_queue.append(lambda : listener.invoke(game_manager, target, previous, current))

    def on_calculate_card_cost(self, game_manager: GameManager, immediate: bool = False):
        if immediate:
            for listener in self.__on_calculate_card_cost:
                listener.invoke(game_manager)
        else:
            for listener in self.__on_calculate_card_cost:
                self.__event_queue.append(lambda : listener.invoke(game_manager))

    def invoke_events(self):
        """이벤트 큐의 모든 이벤트 실행."""
        executing_events = self.__event_queue.copy()
        self.__event_queue.clear()
        while len(executing_events) > 0:
            executing_events.pop(0)()