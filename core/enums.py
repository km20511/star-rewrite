"""
core 모듈에서 사용하는 Enum 자료구조들을 모아 둔 스크립트.
"""
from enum import Enum


class CardType(Enum):
    """카드의 유형. 적, 아이템, 사건 카드로 구분."""
    Enemy = 0
    Item = 1
    Event = 2


class EffectTarget(Enum):
    """
    효과가 영향을 미치는 영역의 유형.
    """

    Executer = 0
    """실행되고 있는 효과가 속해 있는 EffectHolder에서만 발동. '3골드를 얻습니다.'와 같이 효과가 적용되는 객체를 가릴 필요 없이 한 번만 실행하는 효과에 적합함."""

    Target = 1
    """구매 등 특정 카드나 아이템을 대상으로 발동된 경우, 그 대상 EffectHolder에서만 발동."""

    Deck = 2
    """덱에 있는 카드 중에서 효과가 적용되는 객체를 가릴 경우 사용."""

    Inventory = 3
    """인벤토리에 있는 아이템 중에서 효과가 적용되는 객체를 가릴 경우 사용."""


class EventType(Enum):
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
    OnPlayerStatChanged = 32
    """체력, 공격력 등 플레이어 능력치 수치의 변동이 있을 때 발동."""
    OnTurnBegin = 64
    """턴 시작 시 발동."""
    OnTurnEnd = 128
    """턴 종료 시 발동."""
    OnCardCostChanged = 256
    """아이템 카드의 비용이나 적 카드의 체력 변동이 있을 때 발동."""
    OnCardMoved = 512
    """카드의 위치가 변경되었을 때 발동."""