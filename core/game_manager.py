"""
게임의 생성, 진행, 관리 등을 담당하는 스크립트.
"""

import os
import json
from datetime import datetime
from typing import Final, List
from dataclasses import dataclass

import core.card_data_manager as cdm
from core.card import Card
from core.item import Item
from core.deck_manager import Deck
from core.inventory_manager import Inventory
from core.event_manager import EventManager


# 상수
LEVEL_PATH: Final[str] = "data/levels"
SAVEFILE_PATH: Final[str] = "data/savefiles"


@dataclass
class GameState:
    """
    저장, 그리기 등에 사용하는 현재 게임 상태.
    """
    player_money: int = 5,
    player_health: int = 5,
    player_attack: int = 0,
    player_action: int = 3, 
    player_index: int = 0,
    player_remaining_action: int = 3,
    current_turn: int = 1,
    deck: List[Card] = [],
    inventory: List[Item] = []


class GameManager:
    """
    게임의 전체적인 진행을 담당.
    """

    def __init__(self, game_state: GameState, level_name: str) -> None:
        """GameManager의 초기화 메소드. 외부에서 직접 호출하는 것은 권장하지 않음."""
        self.__game_state: GameState = game_state
        self.__level_name: str = level_name
        self.__deck: Deck = Deck(game_state.deck)
        self.__inventory: Inventory = Inventory(game_state.inventory)
        self.__event_manager: EventManager = EventManager()

    @staticmethod
    def create_from_level(path: str) -> "GameManager":
        """level json 파일로부터 새 게임 생성.
        :param path: 파일이 위치한 현재 작업 경로 기준 상대 경로 또는 절대 경로.
        :return: 해당 파일로 설정한 GameManager 객체.
        """
        cdm.initialize()
        with open(path, encoding="utf-8") as f:
            tree: dict = json.load(f)

        state: GameState = GameState()
        if "player_money" in tree: state.player_money = tree["player_money"]
        if "player_health" in tree: state.player_health = tree["player_health"]
        if "player_index" in tree: state.player_index = tree["player_index"]
        if "player_action" in tree: 
            state.player_action = tree["player_action"]
            state.player_remaining_action = tree["player_action"]

        cards: List[Card] = []
        for i in tree["deck"]:
            data = cdm.get_card_data(i)
            if data is None: 
                print(f"Error: 존재하지 않는 카드 ID: {i}")
                continue
            cards.append(Card(data))

        items: List[Item] = []
        for i in tree["inventory"]:
            data = cdm.get_item_data(i)
            if data is None: 
                print(f"Error: 존재하지 않는 아이템 ID: {i}")
                continue
            items.append(Item(data))

        # TODO: boss 처리

    @staticmethod
    def create_from_savefile(path: str) -> "GameManager":
        """이전에 진행한 저장 파일을 불러옴.
        :param path: 파일이 위치한 현재 작업 경로 기준 상대 경로 또는 절대 경로.
        :return: 해당 파일로 설정한 GameManager 객체.
        """
        raise NotImplementedError

    def save(self, path: str) -> None:
        """현재 게임 상태를 주어진 경로의 폴더에 저장."""
        # TODO: 저장 파일 포맷 완성
        tree: dict = {
            "level_name": self.__level_name,
            "datetime": datetime.now().strftime('%Y_%m_%d_%H_%M_%S'),
            **self.__game_state.__dict__ # 나중에 고치시오
        }
        with open(os.path.join(path, f"{self.__level_name}_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.json"), "w", encoding="utf-8") as f:
            json.dump(tree, f)
        raise NotImplementedError

    def get_game_state(self) -> GameState:
        """현재 게임 상태를 반환. 주로 초기화에 사용."""
        return self.__game_state

    def get_draw_events(self):
        """이전 호출 이후로 생긴 게임 상태의 변화 등 이벤트의 목록을 반환."""
        raise NotImplementedError

    def can_buy_card(self, id: int) -> bool:
        """해당 id의 카드를 구매할 수 있는지 검사."""
        raise NotImplementedError

    def buy_card(self, id: int) -> None:
        """(가능하다면) 주어진 id의 카드를 구매함."""
        raise NotImplementedError

    def can_use_item(self, id: int) -> bool:
        """해당 id의 아이템을 사용할 수 있는지 검사."""
        raise NotImplementedError
    
    def use_item(self, id: int) -> None:
        """(가능하다면) 주어진 id의 아이템을 사용함."""
        raise NotImplementedError

    def can_end_turn(self) -> bool:
        """현재 턴을 넘길 수 있는 상태인지 검사."""
        raise NotImplementedError
    
    def end_turn(self) -> None:
        """(가능하다면) 다음 턴으로 넘김."""
        raise NotImplementedError