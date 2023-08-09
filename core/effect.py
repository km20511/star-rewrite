"""
카드나 아이템, 그리고 이 외의 잔류 효과 구현에 필요한 Effect 클래스와 EffectHolder 클래스, 그리고 여기에 사용되는 enum들을 구현한 스크립트.
"""
from uuid import uuid4
from typing import List

from core.card_data_manager import EffectData


class Effect:
    """
    json에서 데이터로 기술된 효과를 구현하며, EffectHolder 객체에 붙여 사용함.
    """
    def __init__(self, owner: "EffectHolder", data: EffectData) -> None:
        self.__id: int = uuid4()
        self.__owner: EffectHolder = owner
        self.__data: EffectData = data

    @property
    def id(self) -> int:
        return self.__id
    
    @property
    def owner(self) -> "EffectHolder":
        return self.__owner
    
    @property
    def data(self) -> EffectData:
        return self.__data
    

class EffectHolder:
    """
    효과들을 관리하며 각 효과를 실행하는 주체를 명확히 함. Card나 Item 클래스는 이를 상속하며, Game 클래스 등에 하나의 객체를 생성해 잔류 효과 구현 가능.
    """
    def __init__(self, effects: List[Effect] = []) -> None:
        self.__id = uuid4().int
        self.__effects: List[Effect] = effects

    @property
    def id(self):
        """ 카드, 아이템 등 객체를 식별하는 고유 id. """
        return self.__id

    def add_effect(self, effect: Effect):
        """Effect를 목록에 추가"""
        if effect not in self.__effects:
            self.__effects.append(effect)

    def has_effect(self, effect: Effect):
        """Effect가 목록에 있는지 확인"""
        return effect in self.__effects
    
    def remove_effect(self, effect: Effect):
        """Effect가 목록에 있다면 제거"""
        if effect in self.__effects:
            self.__effects.remove(effect)