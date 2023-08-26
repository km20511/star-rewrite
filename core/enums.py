"""
core 모듈에서 사용하는 Enum 자료구조들을 모아 둔 스크립트.
"""
from enum import Enum, auto


class PlayerStat(Enum):
    """플레이어 능력치 유형."""
    Money = auto()
    """플레이어가 가진 돈."""
    Health = auto()
    """플레이어의 체력."""
    Attack = auto()
    """플레이어의 공격력."""
    Action = auto()
    """플레이어의 행동력."""


class CardType(Enum):
    """카드의 유형. 적, 아이템, 사건 카드로 구분."""
    Enemy = auto()
    Item  = auto()
    Event = auto()


class EffectTarget(Enum):
    """
    효과가 영향을 미치는 영역의 유형.
    """
    Executer = auto()
    """실행되고 있는 효과가 속해 있는 EffectHolder에서만 발동. '3골드를 얻습니다.'와 같이 효과가 적용되는 객체를 가릴 필요 없이 한 번만 실행하는 효과에 적합함."""
    Deck = auto()
    """덱에 있는 카드 중에서 효과가 적용되는 객체를 가릴 경우 사용."""
    Inventory = auto()
    """인벤토리에 있는 아이템 중에서 효과가 적용되는 객체를 가릴 경우 사용."""


class EventType(Enum):
    """이벤트가 발생하는 경우의 목록."""

    OnShown = auto()
    """카드가 공개되었을 때 발동."""
    OnEntered = auto()
    """카드가 조작 범위 내에 진입했을 때 발동."""
    OnPurchased = auto()
    """카드를 구매했을 때(적의 경우 처치했을 때)  발동"""
    OnUsed = auto()
    """아이템을 사용했을 때 발동."""
    OnCardCreated = auto()
    """카드가 생성되었을 때 발동."""
    OnItemCreated = auto()
    """아이템이 생성되었을 때 발동."""
    OnCardDestroyed = auto()
    """카드가 파괴되었을 때 발동."""
    OnItemDestroyed = auto()
    """아이템이 파괴되었을 때 발동."""
    OnPlayerStatChanged = auto()
    """체력, 공격력 등 플레이어 능력치 수치의 변동이 있을 때 발동."""
    OnTurnBegin = auto()
    """턴 시작 시 발동."""
    OnTurnEnd = auto()
    """턴 종료 시 발동."""
    OnCardCostChanged = auto()
    """아이템 카드의 비용이나 적 카드의 체력 변동이 있을 때 발동."""
    OnCardMoved = auto()
    """카드의 위치가 변경되었을 때 발동."""
    OnCalculateCardCost = auto()
    """카드의 비용을 계산해야 할 때 발동. 지속 효과 전용."""


class DrawEventType(Enum):
    """게임 상태를 그릴 때 사용하는 이벤트의 종류."""
    TurnBegin = auto()
    """새 턴이 시작됨.
    current: 현재 턴."""
    TurnEnd = auto()
    """현재 턴이 종료됨.
    current: 현재 턴."""
    CardCreated = auto()
    """카드가 새로 생성됨.
    target: 생성된 카드 id.
    current: 생성된 인덱스."""
    CardShown = auto()
    """카드가 공개되거나 숨겨짐.
    target: 해당 카드 id.
    previous: 기존 앞면 여부(0/1)
    current: 현재 앞면 여부(0/1)"""
    CardMoved = auto()
    """카드가 이동함.
    target: 해당 카드 id.
    previous: 기존 인덱스.
    current: 현재 인덱스."""
    CardPurchased = auto()
    """카드가 구매됨.
    target: 해당 카드 id."""
    CardDestroyed = auto()
    """카드가 파괴됨.
    target: 해당 카드 id."""
    CardCostChanged = auto()
    """카드 비용이 변화함.
    target: 해당 카드 id.
    previous: 이전 비용.
    current: 현재 비용."""
    ItemCreated = auto()
    """아이템이 새로 생성됨.
    target: 생성된 아이템 id."""
    ItemUsed = auto()
    """아이템이 사용됨.
    target: 해당 아이템 id."""
    ItemDestroyed = auto()
    """아이템이 파괴됨.
    target: 해당 아이템 id."""
    PlayerWon = auto()
    """플레이어가 승리함.
    TODO: 승리/패배 유형 전달."""
    PlayerLost = auto()
    """플레이어가 패배함."""
    PlayerStatChanged = auto()
    """플레이어 상태가 변화함.
    target: 해당 상태의 PlayerType(int).
    previous: 해당 상태의 이전 값.
    current: 해당 상태의 현재 값."""