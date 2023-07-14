"""
카드와 아이템 데이터가 기록된 json 파일에 접근하고 python 자료구조로 파싱하는 스크립트.
"""
import json
from enum import Enum
from typing import List, Dict
from dataclasses import dataclass


class CardType(Enum):
    """카드의 유형. 적, 아이템, 사건 카드로 구분."""
    Enemy = 0
    Item = 1
    Event = 2


@dataclass(frozen=True)
class CardData:
    """카드의 속성을 담는 자료구조."""
    id: int
    name: str
    type: CardType
    cost: int
    sprite_name: str
    description: str
    effects: List[dict]


@dataclass(frozen=True)
class ItemData:
    """아이템의 속성을 담는 자료구조."""
    id: int
    name: str
    sprite_name: str
    description: str
    effects: List[dict]


CARDS_DATA_PATH = "data/cards/cards.json"
"""카드 데이터 파일의 경로. 상수이므로 수정하지 말 것."""

ITEMS_DATA_PATH = "data/cards/items.json"
"""아이템 데이터 파일의 경로. 상수이므로 수정하지 말 것."""

__db_cards: Dict[int, CardData] = {}
"""등록된 카드 데이터의 목록. 외부에서 접근하지 말 것. (대신 get_card_data()를 사용할 것.)"""

__db_items: Dict[int, ItemData] = {}
"""등록된 아이템 데이터의 목록. 외부에서 접근하지 말 것. (대신 get_item_data()를 사용할 것.)"""

def initialize():
    """파일을 불러오고 DB를 초기화하는 함수. 이 모듈을 사용하기 전 호출할 것."""
    __db_cards.clear()
    __db_items.clear()

    with open(CARDS_DATA_PATH, encoding = "utf-8") as f:
        tree_cards: dict = json.load(f)

    for card in tree_cards["contents"]:
        __db_cards[card["id"]] = CardData(
            card["id"],
            card["name"],
            CardType[card["type"]],
            card["cost"],
            card["sprite_name"],
            card["description"],
            card["effects"]
        )

    with open(ITEMS_DATA_PATH, encoding = "utf-8") as f:
        tree_items: dict = json.load(f)
    
    for item in tree_items["contents"]:
        __db_items[item["id"]] = ItemData(
            item["id"],
            item["name"],
            item["sprite_name"],
            item["description"],
            item["effects"]
        )

def get_card_data(id: int) -> CardData:
    """DB에서 주어진 id에 해당하는 카드를 찾아 반환. 찾지 못할 경우 None 반환."""
    return __db_cards.get(id, None)

def get_item_data(id: int) -> ItemData:
    """DB에서 주어진 id에 해당하는 아이템을 찾아 반환. 찾지 못할 경우 None 반환."""
    return __db_items.get(id, None)

def all_cards() -> List[CardData]:
    """불러온 모든 카드 데이터 목록을 반환"""
    return __db_cards.copy()

def all_items() -> List[ItemData]:
    """불러온 모든 아이템 데이터 목록을 반환"""
    return __db_items.copy()

if __name__ == "__main__":
    initialize()