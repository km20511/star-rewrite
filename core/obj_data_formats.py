"""
카드나 아이템, 효과의 상황에 맞는 데이터 양식을 작성한 스크립트.
"""

from dataclasses import dataclass
from typing import Dict, List

from core.enums import CardType, DrawEventType, EffectTarget, EventType


@dataclass(frozen=True)
class EffectData:
    """효과의 속성을 담는 자료구조."""
    event_type: EventType
    effect: str
    target: EffectTarget
    query: str
    order_method: str
    order_crop: str
    args: Dict[str, str]


@dataclass(frozen=True)
class CardData:
    """카드의 속성을 담는 자료구조."""
    id: int
    name: str
    type: CardType
    cost: int
    sprite_name: str
    description: str
    effects: List[EffectData]


@dataclass(frozen=True)
class ItemData:
    """아이템의 속성을 담는 자료구조."""
    id: int
    name: str
    sprite_name: str
    description: str
    effects: List[EffectData]


@dataclass
class EffectSaveData:
    """저장 파일에서 효과를 표현하는 자료구조."""
    id: int
    data: EffectData


@dataclass
class CardSaveData:
    """저장 파일에서 카드를 표현하는 자료구조."""
    data_id: int
    is_front_face: bool
    instant_cost_modifier: int


@dataclass
class ItemSaveData:
    """저장 파일에서 아이템을 표현하는 자료구조."""
    data_id: int


@dataclass
class CardDrawData:
    """외부 모듈이 카드를 그리기 위한 정보."""
    id: int
    name: str
    type: CardType
    base_cost: int
    current_cost: int
    sprite_name: str
    description: str


@dataclass
class ItemDrawData:
    """외부 모듈이 아이템을 그리기 위한 정보."""
    id: int
    name: str
    sprite_name: str
    description: str


@dataclass
class GameDrawState:
    """
    게임 상태를 그리는 외부 모듈에 전달하는 현재 게임 상태.
    """
    player_money: int 
    player_health: int
    player_attack: int
    player_action: int 
    player_index: int 
    player_remaining_action: int
    current_turn: int
    deck: List[CardDrawData]
    inventory: List[ItemDrawData]


@dataclass
class DrawEvent:
    """게임 상태의 변경이 있을 때 외부 모듈에 알리기 위한 이벤트.
    아래 속성은 이벤트의 종류에 따라 다른 역할을 하거나 사용하지 않을 수 있음."""
    event_type: DrawEventType
    target_id: int
    previous: int
    current: int