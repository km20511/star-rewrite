"""
카드나 아이템, 그리고 이 외의 잔류 효과 구현에 필요한 Effect 클래스와 EffectHolder 클래스, 그리고 여기에 사용되는 enum들을 구현한 스크립트.
"""
import json
from enum import Enum
from typing import List


class EffectTarget(Enum):
    """
    효과가 영향을 미치는 영역의 유형.
    """

    Executer = 0
    """실행되고 있는 효과가 속해 있는 EffectHolder에서만 발동. '3골드를 얻습니다.'와 같이 효과가 적용되는 객체를 가릴 필요 없이 한 번만 실행하는 효과에 적합함."""

    Deck = 1
    """덱에 있는 카드 중에서 효과가 적용되는 객체를 가릴 경우 사용."""

    Inventory = 2
    """인벤토리에 있는 아이템 중에서 효과가 적용되는 객체를 가릴 경우 사용."""

    All = 3
    """인벤토리와 덱의 모든 카드와 아이템을 검사. 가급적 추천하지 않음."""


class Effect:
    """
    json에서 데이터로 기술된 효과를 구현하며, EffectHolder 객체에 붙여 사용함.
    """
    def __init__(self, owner, effect: str, effect_target: EffectTarget, query: str = "", order_method: str = "", order_crop: int = 0) -> None:
        """
        :param owner: 이 효과 객체가 속한 EffectHolder 객체
        :param effect: json 파일의 effect 속성. 최종적으로 발동할 효과를 기술한 식. 보안 절차를 거쳐 eval로 호출됨.
        :param effect_target: 이 효과가 적용될 대상을 판단하는 범위. 
        :param query: 해당 범위 내에서 이 효과가 적용될 대상을 판단하는 기준. bool을 반환하는 식이어야 함. 보안 절차를 거쳐 eval로 호출됨. 명시되지 않은 경우 effect_target에 해당하는 모든 객체에 적용됨.
        :param order_method: 뒤의 order_crop과 함께 걸러진 목록에서 효과가 적용되는 객체를 구별하기 위해 사용. int와 같이 비교가 가능한 값을 반환하는 식이어야 함. 보안 절차를 거쳐 eval로 호출됨. 명시되지 않은 경우 정렬을 수행하지 않음.
        :param order_crop: 앞의 order_method를 통해 정렬한 값 중 앞의 몇 개를 거르는 데 사용. (예: '공개된 카드 중 제일 비용이 작은 [order_crop]개의...') 0 이하의 값의 경우 이 과정을 수행하지 않음.
        """
        self.__owner: EffectHolder = owner
        self.__effect: str = effect
        self.__effect_target: EffectTarget = effect_target
        self.__query: str = query
        self.__order_method: str = order_method
        self.__order_crop: int = order_crop

    @staticmethod
    def from_json_dict(owner, tree: dict):
        """
        json 텍스트로부터 Effect 객체를 생성함.
        :param owner: 생성될 객체가 속한 EffectHolder 객체
        :param text: 변환할 json 텍스트. effects 배열에 든 객체를 사용해야 함.
        :return: 변환된 Effect 객체
        """
        return Effect(
            owner,
            tree.get('effect', ''),
            EffectTarget[tree.get('target', '')],   # KeyError 주의
            tree.get('query', ''),
            tree['order_by'].get('value', '') if 'order_by' in tree.keys() else '',
            tree['order_by'].get('crop', 0) if 'order_by' in tree.keys() else 0
        )    

    @property
    def owner(self):
        return self.__owner
    
    @property
    def effect(self):
        return self.__effect
    
    @property
    def effect_target(self):
        return self.__effect_target
    
    @property
    def query(self):
        return self.__query
    
    @property
    def order_method(self):
        return self.__order_method
    
    @property
    def order_crop(self):
        return self.__order_crop
    

class EffectHolder:
    """
    효과들을 관리하며 각 효과를 실행하는 주체를 명확히 함. Card나 Item 클래스는 이를 상속하며, Game 클래스 등에 하나의 객체를 생성해 잔류 효과 구현 가능.
    """
    def __init__(self, effects: List[Effect] = []) -> None:
        self.__effects: List[Effect] = effects

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