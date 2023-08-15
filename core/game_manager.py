"""
게임의 생성, 진행, 관리 등을 담당하는 스크립트.
"""

import os
import json
from datetime import datetime
from typing import Any, Dict, Final, List
from dataclasses import dataclass

import core.card_data_manager as cdm
from core.card import Card
from core.enums import PlayerStat
from core.item import Item
from core.deck_manager import Deck
from core.inventory_manager import Inventory
from core.event_manager import EventManager
from core.obj_data_formats import CardData, CardDrawData, GameDrawState, ItemData, ItemDrawData


# 상수
LEVEL_PATH: Final[str] = "data/levels"
SAVEFILE_PATH: Final[str] = "data/savefiles"


@dataclass
class GameState:
    """
    GameManager에서 내부적으로 사용하는 현재 게임 상태.
    """
    player_money: int = 5
    player_health: int = 5
    player_attack: int = 0
    player_action: int = 3
    player_index: int = 0
    player_remaining_action: int = 3
    current_turn: int = 1


class GameManager:
    """
    게임의 전체적인 진행을 담당.
    """

    def __init__(self, game_state: GameState, level_name: str, card_ids: List[int], item_ids: List[int]) -> None:
        """GameManager의 초기화 메소드. 외부에서 직접 호출하는 것은 권장하지 않음."""
        self.__game_state: GameState = game_state
        self.__level_name: str = level_name
        self.__event_manager: EventManager = EventManager(self)
        
        cards: List[CardData] = [data for data in map(cdm.get_card_data,card_ids) if data is not None]
        items: List[ItemData] = [data for data in map(cdm.get_item_data,item_ids) if data is not None]
        
        # for i in card_ids:
        #     data = cdm.get_card_data(i)
        #     if data is None: 
        #         print(f"Error: 존재하지 않는 카드 ID: {i}")
        #         continue
        #     cards.append(data)

        # for i in item_ids:
        #     data = cdm.get_item_data(i)
        #     if data is None: 
        #         print(f"Error: 존재하지 않는 아이템 ID: {i}")
        #         continue
        #     items.append(data)

        self.__deck: Deck = Deck(self.__event_manager, cards, game_state.player_index)
        self.__inventory: Inventory = Inventory(self.__event_manager, items)

    @property
    def level_name(self) -> str:
        """현재 게임 레벨의 이름."""
        return self.__level_name
    
    @property
    def deck(self) -> Deck:
        """현재 게임의 덱."""
        return self.__deck
    
    @property
    def inventory(self) -> Inventory:
        """현재 게임의 인벤토리."""
        return self.__inventory

    @property
    def event_manager(self) -> EventManager:
        """이 객체가 사용 중인 EventManager."""
        return self.__event_manager

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


        return GameManager(state, tree["level_name"], tree["deck"], tree["inventory"])

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
        with open(
            os.path.join(path, f"{self.__level_name}_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.json"), 
            "w", encoding="utf-8") as f:
            json.dump(tree, f)
        raise NotImplementedError

    def get_game_draw_state(self) -> GameDrawState:
        """현재 게임 상태를 반환. 주로 초기화에 사용."""
        self.__event_manager.on_calculate_card_cost(True)
        return GameDrawState(
            self.__game_state.player_money,
            self.__game_state.player_health,
            self.__game_state.player_attack,
            self.__game_state.player_action,
            self.__game_state.player_index,
            self.__game_state.player_remaining_action,
            self.__game_state.current_turn,
            [CardDrawData(
                card.id,
                card.card_data.name,
                card.card_data.type,
                card.card_data.cost,
                card.modified_cost,
                card.card_data.sprite_name,
                card.card_data.description
            ) for card in self.__deck.get_cards()],
            [ItemDrawData(
                item.id,
                item.item_data.name,
                item.item_data.sprite_name,
                item.item_data.description
            ) for item in self.__inventory.get_items()]
        )

    def get_draw_events(self):
        """이전 호출 이후로 생긴 게임 상태의 변화 등 이벤트의 목록을 반환."""
        raise NotImplementedError

    def get_readable_static_table(self) -> Dict[str, Any]:
        """효과 스크립팅에서 사용 가능한 정적 변수/함수 목록 반환(읽기 전용)."""
        return {
            "PLAYER_MONEY": PlayerStat.Money,
            "PLAYER_HEALTH": PlayerStat.Health,
            "PLAYER_ATTACK": PlayerStat.Attack,
            "PLAYER_ACTION": PlayerStat.Action,
            "get_player_stat": lambda x: {
                    PlayerStat.Money: self.__game_state.player_money,
                    PlayerStat.Health: self.__game_state.player_health,
                    PlayerStat.Attack: self.__game_state.player_attack,
                    PlayerStat.Action: self.__game_state.player_action
                }.get(x),
            "get_card_data": cdm.get_card_data,
            "get_item_data": cdm.get_item_data,
            "abs": abs,
            "len": len
        }

    def get_writable_static_table(self) -> Dict[str, Any]:
        """효과 스크립팅에서 사용 가능한 정적 변수/함수 목록 반환(쓰기 전용)."""
        return {
            "modify_player_stat": self.modify_player_stat,
            "add_item": self.add_item
        }
    
    def modify_player_stat(self, value_type: PlayerStat, amount: int) -> None:
        """해당 플레이어 능력치를 amount만큼 변화."""
        raise NotImplementedError

    def add_item(self, item_data: ItemData, amount: int = 1):
        """인벤토리에 아이템을 amount개만큼 추가."""
        for i in range(amount):
            self.inventory.add_item(item_data)

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