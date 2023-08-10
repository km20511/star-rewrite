"""
카드와 아이템 데이터가 기록된 json 파일에 접근하고 python 자료구조로 파싱하는 스크립트.
"""
import os
import json
from typing import Final, List, Dict
from dataclasses import dataclass

from core.enums import CardType, EffectTarget, EventType

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


CARDS_DATA_PATH: Final[str] = "data/cards"
"""카드 데이터의 경로. 상수이므로 수정하지 말 것."""

ITEMS_DATA_PATH: Final[str] = "data/items"
"""아이템 데이터의 경로. 상수이므로 수정하지 말 것."""

EFFECTS_DATA_PATH: Final[str] = "data/effects"
"""효과 데이터의 경로. 상수이므로 수정하지 말 것."""

__db_cards: Dict[int, CardData] = {}
"""등록된 카드 데이터의 목록. 외부에서 접근하지 말 것. (대신 get_card_data()를 사용할 것.)"""

__db_items: Dict[int, ItemData] = {}
"""등록된 아이템 데이터의 목록. 외부에서 접근하지 말 것. (대신 get_item_data()를 사용할 것.)"""

__db_effects: Dict[str, EffectData] = {}
"""등록된 효과 데이터의 목록. 외부에서 접근하지 말 것. (대신 get_effect_data()를 사용할 것.)"""


def _full_data_path(path: str) -> str:
    """데이터의 경로를 절대 경로로 변환."""
    return os.path.join(os.getcwd(), path)


def _parse_effect_list(effects: List[dict]) -> List[EffectData]:
    """
    카드, 아이템 데이터의 효과 리스트를 해석해 EffectData 객체의 목록으로 변환.
    id가 주어진 경우 __db_effects에서 데이터를 불러옴.
    """
    result: List[EffectData] = []
    for raw_data in effects:
        if "base_id" in raw_data:
            base: EffectData = __db_effects[raw_data["base_id"]]
            result.append(EffectData(
                raw_data["event_type"]         if "event_type" in raw_data else base.event_type,
                raw_data["effect"]             if "effect"     in raw_data else base.effect,
                raw_data["target"]             if "target"     in raw_data else base.target,
                raw_data["query"]              if "query"      in raw_data else base.query,
                raw_data["order_by"]["method"] if "order_by"   in raw_data else base.order_method,
                raw_data["order_by"]["crop"]   if "order_by"   in raw_data else base.order_crop,
                base.args | {k:v for k, v in raw_data["args"].items() if k in base.args}
                if "args" in raw_data else base.args
            ))
        else:
            result.append(EffectData(
                raw_data["event_type"],
                raw_data["effect"],
                raw_data["target"],
                raw_data["query"]              if "query"      in raw_data else "",
                raw_data["order_by"]["method"] if "order_by"   in raw_data else "",
                raw_data["order_by"]["crop"]   if "order_by"   in raw_data else -1,
                {}
            ))
    return result


def initialize():
    """파일을 불러오고 DB를 초기화하는 함수. 이 모듈을 사용하기 전 호출할 것."""
    __db_cards.clear()
    __db_items.clear()
    __db_effects.clear()

    # 효과 데이터 폴더 내 모든 json 파일 읽기
    full_effect_path: str = _full_data_path(EFFECTS_DATA_PATH)
    effect_files: List[str] = os.listdir(EFFECTS_DATA_PATH)
    for filename in effect_files:
        if not filename.endswith(".json"):
            continue

        with open(os.path.join(full_effect_path, filename), encoding="utf-8") as f:
            tree_effects: dict = json.load(f)

        for effect in tree_effects["contents"]:
            __db_effects[effect["id"]] = EffectData(
                EventType[effect["event_type"]],
                effect["effect"],
                EffectTarget[effect["target"]],
                effect["query"] if "query" in effect else "",
                effect["order_by"]["method"] if "order_by" in effect else "",
                effect["order_by"]["crop"] if "order_by" in effect else -1,
                effect["args"]
            )

    # 카드 데이터 폴더 내 모든 json 파일 읽기
    full_card_path: str = _full_data_path(CARDS_DATA_PATH)
    card_files: List[str] = os.listdir(full_card_path)
    for filename in card_files:
        if not filename.endswith(".json"):
            continue

        with open(os.path.join(full_card_path, filename), encoding="utf-8") as f:
            tree_cards: dict = json.load(f)

        for card in tree_cards["contents"]:
            print(f"Debug: {card['name']}")
            __db_cards[card["id"]] = CardData(
                card["id"],
                card["name"],
                CardType[card["type"]],
                card["cost"],
                card["sprite_name"],
                card["description"],
                _parse_effect_list(card["effects"])
            )

    # 아이템 데이터 폴더 내 모든 json 파일 읽기
    full_item_path: str = _full_data_path(ITEMS_DATA_PATH)
    item_files: List[str] = os.listdir(full_item_path)
    for filename in item_files:
        if not filename.endswith(".json"):
            continue

        with open(os.path.join(full_item_path, filename), encoding="utf-8") as f:
            tree_items: dict = json.load(f)

        for item in tree_items["contents"]:
            __db_items[item["id"]] = ItemData(
                item["id"],
                item["name"],
                item["sprite_name"],
                item["description"],
                _parse_effect_list(item["effects"])
            )


def get_card_data(id: int) -> CardData:
    """DB에서 주어진 id에 해당하는 카드를 찾아 반환. 찾지 못할 경우 None 반환."""
    return __db_cards.get(id, None)

def get_item_data(id: int) -> ItemData:
    """DB에서 주어진 id에 해당하는 아이템을 찾아 반환. 찾지 못할 경우 None 반환."""
    return __db_items.get(id, None)

def get_effect_data(id: str) -> EffectData:
    """DB에서 주어진 id에 해당하는 효과를 찾아 반환. 찾지 못할 경우 None 반환."""
    return __db_effects.get(id, None)

def all_cards() -> List[CardData]:
    """불러온 모든 카드 데이터 목록을 반환."""
    return __db_cards.copy()

def all_items() -> List[ItemData]:
    """불러온 모든 아이템 데이터 목록을 반환."""
    return __db_items.copy()

def all_effects() -> List[EffectData]:
    """불러온 모든 효과 데이터 목록을 반환."""
    return __db_effects.copy()


if __name__ == "__main__":
    initialize()
