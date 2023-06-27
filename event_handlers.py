from enum import Enum
from abc import ABCMeta, abstractmethod

class EventHandlerFlag(Enum):
    """이벤트가 발생하는 경우의 목록. 특정 카드가 이 이벤트를 구독하는지 판단할 때 사용."""

    OnShown = 1
    """카드가 공개되었을 때 발동."""
    OnEntered = 2
    """카드가 조작 범위 내에 진입했을 때 발동."""
    OnPurchased = 4
    """카드를 구매했을 때(적의 경우 처치했을 때)  발동"""
    OnUsed = 8
    """아이템을 사용했을 때 발동."""
    OnDestroyed = 16
    """카드나 아이템이 파괴되었을 때 발동."""
    OnValueChanged = 32
    """체력, 공격력 등 어떤 수치의 변동이 있을 때 발동."""
    OnBeganTurn = 64
    """턴 시작 시 발동."""
    OnEndTurn = 128
    """턴 종료 시 발동."""


"""
# 1안: 이벤트 핸들러 클래스 통일
class EventHandler(metaclass = ABCMeta):
    @abstractmethod
    def on_event(self, event_type: EventHandlerFlag, **kwargs):
        pass

"""
# TODO: 각 이벤트 메소드 인수 확정
# 2안: 클래스 분리

class OnShownEventHandler(metaclass = ABCMeta):
    @abstractmethod
    def on_shown(self):
        pass


class OnEnteredEventHandler(metaclass = ABCMeta):
    @abstractmethod
    def on_entered(self):
        pass


class OnPurchasedEventHandler(metaclass = ABCMeta):
    @abstractmethod
    def on_purchased(self):
            pass


class OnUsedEventHandler(metaclass = ABCMeta):
    @abstractmethod
    def on_used(self):
        pass


class OnDestroyedEventHandler(metaclass = ABCMeta):
    @abstractmethod
    def on_destroyed(self):
        pass


class OnValueChangedEventHandler(metaclass = ABCMeta):
    @abstractmethod
    def on_value_changed(self):
        pass


class OnBeganTurnEventHandler(metaclass = ABCMeta):
    @abstractmethod
    def on_began_turn(self):
        pass


class OnEndTurnEventHandler(metaclass = ABCMeta):
    @abstractmethod
    def on_end_turn(self):
        pass
