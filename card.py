import uuid
from enum import Enum
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


class Card():
    # json db에서 불러올 수 있을 것.
    def __init__(self, card_data: CardData):
        self.__id: int = uuid.uuid4().int
        self.__card_data = __card_data

