"""발생한 이벤트를 효과에 전달하는 인터페이스 역할의 스크립트."""
from enum import Enum
from typing import TYPE_CHECKING, Callable, TypeVar, Generic

from core.card import Card
from core.item import Item
from core.effect import Effect
from core.enums import PlayerStat
if TYPE_CHECKING:
    from core.game_manager import GameManager


# 이벤트 인수용 타입 변수 (확장 시 타입 추가 바람.)
T = TypeVar("T", Card, Item, PlayerStat, int)
U = TypeVar("U", Card, Item, PlayerStat, int)
V = TypeVar("V", Card, Item, PlayerStat, int)


class EventHandlerBase():
    """이벤트 클래스의 기본 형태."""
    def __init__(self, owner: Effect) -> None:
        self.__owner: Effect = owner

    @property
    def owner(self) -> Effect:
        return self.__owner


class EventHandler0(EventHandlerBase):
    """인수 없는 이벤트 클래스."""
    def __init__(self, owner: Effect, listener: Callable[["GameManager"], None]) -> None:
        super().__init__(owner)
        self.__listener: Callable[["GameManager"], None] = listener

    def invoke(self, game_manager: "GameManager") -> None:
        self.__listener(game_manager)


class EventHandler1(EventHandlerBase, Generic[T]):
    """인수 1개의 이벤트 클래스."""
    def __init__(self, owner: Effect, listener: Callable[["GameManager", T], None]) -> None:
        super().__init__(owner)
        self.__listener: Callable[["GameManager", T], None] = listener

    def invoke(self, game_manager: "GameManager", arg: T) -> None:
        self.__listener(game_manager, arg)


class EventHandler2(EventHandlerBase, Generic[T, U]):
    """인수 2개의 이벤트 클래스."""
    def __init__(self, owner: Effect, listener: Callable[["GameManager", T, U], None]) -> None:
        super().__init__(owner)
        self.__listener: Callable[["GameManager", T, U], None] = listener

    def invoke(self, game_manager: "GameManager", arg0: T, arg1: U) -> None:
        self.__listener(game_manager, arg0, arg1)


class EventHandler3(EventHandlerBase, Generic[T, U, V]):
    """인수 3개의 이벤트 클래스."""
    def __init__(self, owner: Effect, listener: Callable[["GameManager", T, U, V], None]) -> None:
        super().__init__(owner)
        self.__listener: Callable[["GameManager", T, U, V], None] = listener

    def invoke(self, game_manager: "GameManager", arg0: T, arg1: U, arg2: V) -> None:
        self.__listener(game_manager, arg0, arg1, arg2)


# class OnShownEventHandler(EventHandler1[Card]):
#     """카드가 공개된 경우 발동하는 이벤트. 공개되는 카드를 인수로 받음."""


# class OnEnteredEventHandler(EventHandler1[Card]):
#     """카드가 현재 시점(조작 가능한 3칸)에 진입한 경우 발생하는 이벤트. 진입한 카드를 인수로 받음."""


# class OnPurchasedEventHandler(EventHandler1[Card]):
#     """카드가 구매/처치되었을 경우 발생하는 이벤트. 구매된 카드를 인수로 받음."""


# class OnUsedEventHandler(EventHandler1[Item]):
#     """아이템이 사용되었을 경우 발생하는 이벤트. 해당 아이템을 인수로 받음."""


# class OnDestroyedEventHandler(EventHandler1[Card]):
#     """카드가 효과 등으로 파괴되었을 때 발생하는 이벤트. 해당 카드를 인수로 받음."""


# class OnValueChangedEventHandler(EventHandlerBase):
#     def on_value_changed(self):
#         pass


# class OnBeganTurnEventHandler(EventHandler1[int]):
#     """턴이 시작되었을 경우 발생하는 이벤트. 현재 턴 수를 인수로 받음."""


# class OnEndTurnEventHandler(EventHandler1[int]):
#     """턴이 종료되었을 경우 발생하는 이벤트. 현재 턴 수를 인수로 받음."""
