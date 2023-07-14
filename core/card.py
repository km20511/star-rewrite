from . import effect
from . import card_data_manager as card_data


class Card(effect.EffectHolder):
    """
    덱에 존재하는 카드 클래스.
    """
    def __init__(self, data: card_data.CardData, index:int = -1):
        """
        :param data: 이 카드에 표시되는 데이터.
        :param index: 이 카드가 덱에서 존재하는 위치. *실제 위치와 동일해야 함. 수시로 갱신해 동기화할 것.*
        """
        self.__card_data = data
        self.__current_index = index
        self.__previous_index = index
        self.__modified_cost = data.cost
        super().__init__(data.effects)

    def __repr__(self) -> str:
        return f"Card {{ '{self.__card_data.name} [{self.__card_data.type.name}]' ({f'*{self.modified_cost}*' if self.modified_cost != self.__card_data.cost else self.modified_cost})}}"

    @property
    def card_data(self):
        return self.__card_data

    @property
    def current_index(self):
        return self.__current_index
    
    @property
    def previous_index(self):
        return self.__previous_index
    
    @property
    def modified_cost(self):
        return self.__modified_cost

    @modified_cost.setter
    def modified_cost(self, cost: int):
        self.__modified_cost = cost if cost >= 0 else 0
    
    def set_index(self, index: int, init: bool = False):
        """
        이 카드의 덱에서의 인덱스를 설정함.
        :param index: 설정할 위치 값.
        :param init: 참인 경우, '초기화'로 간주하고 현재/이전 위치 모두를 이 값으로 변경함. 거짓인 경우, '이동'으로 간주하고 현재 값만 이 값을 할당, 이전 값은 현재 값의 이전 값이 됨.
        """
        if init:
            self.__previous_index = self.__current_index = index
        else:
            self.__previous_index = self.__current_index
            self.__current_index = index