"""
게임 내 덱을 관리하는 스크립트.
"""
from random import shuffle
from typing import List, Callable, Optional, Set

from .card import Card
from .utils import Comparable
from .card_data_manager import CardData


class Deck:
    """
    게임 속 카드가 나열된 덱.
    이 게임에서는 플레이어가 활동하는 전장의 역할도 한다.
    덱에 있는 카드를 관리하고, 효과 스크립트가 조건에 맞게 카드를 조작할 수 있는 메소드를 제공한다.
    """
    def __init__(self, deck: List[Card], player_index: int = 0) -> None:
        self.__deck: List[Card] = deck.copy()
        self.__player_index: int = player_index
        for ind, card in enumerate(self.__deck):
            card.set_index(ind, init = True)

    @property
    def player_index(self):
        """
        플레이어가 덱에 위치하는 인덱스.
        이를 기반으로 카드의 시간대 등을 결정한다.
        """
        return self.__player_index

    def update_index(self, init: bool = False):
        """
        카드에 저장된 인덱스 데이터 갱신. 
        :param init: 초기화/이동 여부.
        """
        for ind, card in enumerate(self.__deck):
            card.set_index(ind, init) 

    def get_cards(self, query: Callable[[Card], bool] = None) -> List[Card]:
        """조건에 맞는 카드를 순서를 유지해 반환."""
        return list(filter(query, self.__deck)) if query is not None else self.__deck.copy()
    
    def print_table(self, query: Callable[[Card], bool] = None, header: bool = True) -> str:
        """
        조건에 맞는 카드들의 정보를 표 양식의 문자열로 반환하는 디버그용 함수.
        열 구성: 순번, 이름, 유형, 현재 인덱스, 이전 인덱스, 비용
        """
        result: str = "(순번, 이름, 유형, 현재 위치, 이전 위치, 비용)\n" if header else ""
        for ind, card in enumerate(filter(query, self.__deck) if query is not None else self.__deck):
            result += f"{ind:>2d} {card.card_data.name:20s}\t{card.card_data.type.name:>5s} {card.current_index:>2d} {card.previous_index:>2d} {f'*{card.modified_cost}*' if card.modified_cost != card.card_data.cost else f'{card.modified_cost}':>4s}\n"
        return result.strip()

    # 아래 메소드들은 효과가 실행될 때 사용됨.

    def create_query(self) -> "DeckQuery":
        """이 덱을 대상으로 하는 DeckQuery 객체 생성."""
        return DeckQuery(self)
    
    def shuffle_cards(self, query: "DeckQuery"):
        """조건에 맞는 카드를 서로 섞음."""
        target_ids: Set[int] = query.get_target_from(self.__deck)
        mask: List[bool] = [card.id in target_ids for card in self.__deck]
        target: List[Card] = [card for ind, card in enumerate(self.__deck) if mask[ind]]
        shuffled_target: List[Card] = target.copy()

        while target == shuffled_target: # 같은 배열로 섞이는 것 방지
            shuffle(shuffled_target)
        
        result: List[Card] = [
            (shuffled_target.pop(0) if mask[ind] else card) 
            for ind, card in enumerate(self.__deck)
        ]
        
        self.__deck = result 
        self.update_index(init = False)

    def shift_cards(self, query: "DeckQuery", shift: int):
        """
        조건에 맞는 카드를 주어진 수만큼 이동시킴.
        TODO: player_index 대응
        """
        if shift == 0 or query is None:
            return
        
        # 이동의 대상이 되는 카드 목록.
        target: List[Card] = []
        # 이동 대상이 아닌 카드 목록.
        non_target: List[Card] = []
        # 이동 대상 카드들의 인덱스.
        index_table: List[int] = []

        target_ids: Set[int] = query.get_target_from(self.__deck)

        for k, v in enumerate(self.__deck):
            if v.id in target_ids:
                target.append(v)
                index_table.append(k)
            else:
                non_target.append(v)

        target_count: int = len(index_table)
        if shift > 0: # 우측으로 이동
            maximum_index: int = len(self.__deck) - 1
            for i in range(target_count - 1, -1, -1):
                # 이동 중 플레이어를 지나쳤다면 플레이어 위치 수정
                if index_table[i] < self.__player_index <= index_table[i] + shift:
                    self.__player_index -= 1
                index_table[i] = min(index_table[i] + shift, maximum_index)
                maximum_index = index_table[i] - 1
        else:
            minimum_index: int = 0
            for i in range(target_count):
                # 이동 중 플레이어를 지나쳤다면 플레이어 위치 수정
                if index_table[i] + shift < self.__player_index <= index_table[i]:
                    self.__player_index += 1
                index_table[i] = max(index_table[i] + shift, minimum_index)
                minimum_index = index_table[i] + 1
        
        result: List[Card] = [
            (target.pop(0) if i in index_table else non_target.pop(0)) 
            for i in range(len(self.__deck))
        ]
        self.__deck = result
        self.update_index(init = False)

    def insert_cards(self, query: "DeckQuery", card: Callable[[Card], CardData]):
        """조건에 맞는 카드의 왼쪽에 새로운 카드 추가."""
        raise NotImplementedError()
    
    def destroy_cards(self, query: "DeckQuery"):
        """조건에 맞는 카드를 파괴. 구매/처치에 해당하지 않음."""
        target_ids: Set[int] = query.get_target_from(self.__deck)
        result: List[Card] = self.__deck.copy()
        for k, v in enumerate(self.__deck):
            if v.id not in target_ids:
                continue
            if k < self.__player_index:
                self.__player_index -= 1
            result.remove(v)
        self.__deck = result

    def show_cards(self, query: "DeckQuery", show: bool = True):
        """조건에 맞는 카드를 공개(앞면)/비공개(뒷면) 처리."""
        target_ids: Set[int] = query.get_target_from(self.__deck)
        for card in self.__deck:
            if card.id in target_ids:
                card.is_front_face = show

    def modify_card_cost(self, query: "DeckQuery", amount: int):
        """조건에 맞는 카드의 비용을 변동시킴. 일회성 효과 전용."""
        target_ids: Set[int] = query.get_target_from(self.__deck)
        for card in self.__deck:
            if card.id in target_ids:
                card.instant_cost_modifier += amount
                


class DeckQuery:
    """
    덱의 카드를 선택하는 조건을 관리.
    직접 생성자를 호출하기보다 Deck.create_query()를 사용하는 것을 권장.
    """
    def __init__(self, deck: Deck) -> None:
        """
        DeckQuery의 초기화 함수.
        직접 객체를 생성하기보다 Deck.create_query()를 사용하는 것을 권장.
        :param deck: Query를 적용할 덱.
        """
        self.__deck: Deck = deck
        self.__query: Optional[Callable[[Card], bool]] = None
        self.__order_method: Optional[Callable[[Card], Comparable]] = None
        self.__order_crop: int = -1
    
    def set_query(self, query: Callable[[Card], bool]) -> "DeckQuery":
        """
        카드를 검사할 조건을 추가.
        :param query: 추가할 조건. Card를 인수로 받아 bool을 반환해야 함.
        :return: chaining 구현을 위해 자기 자신 반환.
        """
        self.__query = query
        return self
    
    def set_order(self, order_method: Callable[[Card], Comparable], order_crop: int) -> "DeckQuery":
        """
        카드를 상위 몇 개까지 걸러내는 형태의 조건 추가.
        예시: '플레이어로부터 가장 가까운 3개의 카드 ...'
        :param order_method: 정렬 기준. Card를 인수로 받아 비교 가능한 객체(sorted의 key와 동일)를 반환해야 함. 효과 적용 순서와는 무관.
        :param order_crop: 정렬된 대상을 상위 몇 개까지 선택할지 결정. 자연수가 아닌 경우 조건 추가가 이루어지지 않음.
        :return: chaining 구현을 위해 자기 자신 반환.
        """
        if order_crop > 0:
            self.__order_method = order_method
            self.__order_crop = order_crop
        return self

    def get_target_from(self, cards: List[Card]) -> Set[int]:
        """
        주어진 목록에서 지정한 조건을 전부 만족하는 카드 집합을 반환.
        :return: 조건을 만족하는 카드의 id 집합.
        """
        if self.__query is not None:
            cards = list(filter(self.__query, cards))
        if self.__order_method is not None and self.__order_crop > 0:
            cards = sorted(cards, key=self.__order_method)[:self.__order_crop]
        return {card.id for card in cards}

    def get_target(self) -> Set[int]:
        """
        지정한 조건을 전부 만족하는 덱의 카드 집합을 반환.
        :return: 조건을 만족하는 카드의 id 집합.
        """
        cards: List[Card] = self.__deck.get_cards(self.__query)
        if self.__order_method is not None and self.__order_crop > 0:
            cards = sorted(cards, key=self.__order_method)[:self.__order_crop]
        return {card.id for card in cards}
