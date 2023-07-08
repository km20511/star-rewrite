"""
카드와 아이템 데이터가 기록된 json 파일에 접근하고 python 자료구조로 파싱하는 스크립트.
"""
import json
from enum import Enum
from dataclasses import dataclass


class CardType(Enum):
    Enemy = 0
    Item = 1
    Event = 2


@dataclass(frozen=True)
class CardData:
    id: int
    name: str
    type: CardType
    cost: int
    sprite_name: str
    description: str
    effects: dict


@dataclass
class ItemData:
    id: int
    name: str
    sprite_name: str
    description: str
    effects: dict