"""발생한 이벤트를 효과에 전달하는 인터페이스 역할의 스크립트."""
from enum import Enum
from typing import Callable, List, Protocol, TypeVar, Generic, TYPE_CHECKING

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

EventHandlerType_co = TypeVar("EventHandlerType_co", bound=EventHandlerBase, contravariant=True)

class EventHandlerList(Protocol[EventHandlerType_co]): 
    def append(self, obj: EventHandlerType_co):
        pass
    def remove(self, obj: EventHandlerType_co):
        pass
    def __iter__(self):
        pass
    def clear(self):
        pass

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