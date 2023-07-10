import effect
from enum import Enum
from typing import List
from dataclasses import dataclass


class CardType(Enum):
    Enemy: int = 0
    Item: int = 1
    Event: int = 2


@dataclass(frozen=True)
class CardData():
    name: str
    cost: int
    img_path: str
    card_type: CardType
    description: str


class Card(effect.EffectHolder):
    """
    덱에 존재하는 카드 클래스.
    """
    def __init__(self, effects: List[effect.Effect] = []):
        super().__init__(effects)

