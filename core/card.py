""" 덱의 카드를 표현하는 객체를 구현한 스크립트. """
from core.effect import Effect, EffectHolder
from core.obj_data_formats import CardData, CardSaveData


class Card(EffectHolder):
    """
    덱에 존재하는 카드 클래스.
    """
    def __init__(self, data: CardData, index:int = -1):
        """ Card의 초기화 메소드.
        :param data: 이 카드에 표시되는 데이터.
        :param index: 이 카드가 덱에서 존재하는 위치. *실제 위치와 동일해야 함. 수시로 갱신해 동기화할 것.*
        """
        self.__card_data = data
        self.__current_index = index
        self.__previous_index = index
        self.__modified_cost = data.cost
        self.__instant_cost_modifier = 0
        self.__is_front_face = False
        super().__init__([Effect(self, effect_data) for effect_data in data.effects])

    def __repr__(self) -> str:
        return f"Card {{ '{self.__card_data.name} [{self.__card_data.type.name}]' ({f'*{self.modified_cost}*' if self.modified_cost != self.__card_data.cost else self.modified_cost})}}"

    @property
    def card_data(self):
        """ 카드의 이름, 이미지, 설명, 효과 등 이 카드 '종류'가 갖는 공통적인 테이터 속성. """
        return self.__card_data
    
    @property
    def current_index(self):
        """ 카드가 현재 덱에서 자리하고 있는 위치. """
        return self.__current_index
    
    @property
    def previous_index(self):
        """ 카드가 직전 상태에서 덱에 자리하고 있던 위치. """
        return self.__previous_index
    
    @property
    def modified_cost(self):
        """ 효과 등을 반영해 실제로 적용되는 카드의 비용(적 카드의 경우 체력). """
        return self.__modified_cost

    @modified_cost.setter
    def modified_cost(self, cost: int):
        self.__modified_cost = cost

    @property
    def instant_cost_modifier(self):
        """ 일회성 효과에 의한 카드 비용 변화량. 지속 효과 이후에 적용됨. """
        return self.__instant_cost_modifier
    
    @instant_cost_modifier.setter
    def instant_cost_modifier(self, value: int):
        self.__instant_cost_modifier = value

    @property
    def is_front_face(self):
        """ 카드가 현재 앞면을 보이고 있는지 여부. """
        return self.__is_front_face
    
    @is_front_face.setter
    def is_front_face(self, front: bool):
        self.__is_front_face = front

    @staticmethod
    def from_save_data(card_data: CardData, data: CardSaveData, index: int = -1) -> "Card":
        card = Card(card_data, index)
        card.instant_cost_modifier = data.instant_cost_modifier
        card.is_front_face = data.is_front_face
        return card

    def to_save_data(self) -> CardSaveData:
        return CardSaveData(self.card_data.id, self.is_front_face, self.instant_cost_modifier)
    
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