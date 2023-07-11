"""
게임 내 덱을 관리하는 스크립트.
"""
from card import Card
from typing import List, Callable
from random import shuffle


class Deck:
    """덱의 카드를 저장하고 관리하는 클래스."""
    def __init__(self, deck: List[Card]) -> None:
        self.__deck: List[Card] = deck.copy()
        for ind, card in enumerate(self.__deck):
            card.set_index(ind, init = True)

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
    
    def shuffle_cards(self, query: Callable[[Card], bool] = None):
        """조건에 맞는 카드를 서로 섞음."""
        mask: List[bool] = [query(i) for i in self.__deck]
        target: List[Card] = [card for ind, card in enumerate(self.__deck) if mask[ind]]
        shuffle(target)
        result: List[Card] = [(target.pop(0) if mask[ind] else card) for ind, card in enumerate(self.__deck)]
        self.__deck = result 

    def shift_cards(self, shift:int, query: Callable[[Card], bool] = None):
        """조건에 맞는 카드를 주어진 수만큼 이동시킴."""
        if shift == 0 or query is None:
            return
        target: List[Card] = []
        non_target: List[Card] = []
        index_table: List[int] = []

        for k, v in enumerate(self.__deck):
            if query(v):
                target.append(v)
                index_table.append(k)
            else:
                non_target.append(v)

        target_count: int = len(index_table)
        if shift > 0: # 우측으로 이동
            maximum_index: int = len(self.__deck) - 1
            for i in range(target_count - 1, -1, -1):
                index_table[i] = min(index_table[i] + shift, maximum_index)
                maximum_index = index_table[i] - 1
        else:
            minimum_index: int = 0
            for i in range(target_count):
                index_table[i] = max(index_table[i] + shift, minimum_index)
                minimum_index = index_table[i] + 1
        
        result: List[Card] = [(target.pop(0) if i in index_table else non_target.pop(0)) for i in range(len(self.__deck))]
        self.__deck = result