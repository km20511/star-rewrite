"""
게임의 생성, 진행, 관리 등을 담당하는 스크립트.
"""

import os
import json
from datetime import datetime
from typing import Any, Dict, Final, List, Optional, Tuple
from dataclasses import dataclass
from functools import partial

import core.card_data_manager as cdm
from core.card import Card
from core.enums import CardType, DrawEventType, PlayerStat
from core.item import Item
from core.deck_manager import Deck
from core.inventory_manager import Inventory
from core.event_manager import EventManager
from core.obj_data_formats import (
    CardData, CardDrawData, CardSaveData, DrawEvent, 
    GameDrawState, ItemData, ItemDrawData, ItemSaveData
)


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

    def __init__(self, game_state: GameState, level_name: str, card_saves: List[CardSaveData], item_saves: List[ItemSaveData]) -> None:
        """GameManager의 초기화 메소드. 외부에서 직접 호출하는 것은 권장하지 않음."""
        self.__game_state: GameState = game_state
        self.__level_name: str = level_name
        self.__event_manager: EventManager = EventManager(self)
        
        cards: List[Tuple[CardData, CardSaveData]] = [(data, save) 
            for data, save in map(
            lambda card_save: (cdm.get_card_data(card_save.data_id), card_save),
            card_saves) 
            if data is not None
        ]
        items: List[Tuple[ItemData, ItemSaveData]] = [(data, save) 
            for data, save in map(
            lambda item_save: (cdm.get_item_data(item_save.data_id), item_save),
            item_saves) 
            if data is not None
        ]
        
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

        self.__game_end: bool = False

        self.start_game()

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
    
    @property
    def game_end(self) -> bool:
        return self.__game_end

    @staticmethod
    def create_from_file(path: str) -> "GameManager":
        """level json 파일로부터 새 게임 생성.
        :param path: 파일이 위치한 현재 작업 경로 기준 상대 경로 또는 절대 경로.
        :return: 해당 파일로 설정한 GameManager 객체.
        """
        cdm.initialize()
        with open(path, encoding="utf-8") as f:
            tree: dict = json.load(f)

        state: GameState = GameState()
        if "current_turn" in tree: state.current_turn = tree["current_turn"]
        if "player_money" in tree: state.player_money = tree["player_money"]
        if "player_health" in tree: state.player_health = tree["player_health"]
        if "player_index" in tree: state.player_index = tree["player_index"]
        if "player_attack" in tree: state.player_attack = tree["player_attack"]
        if "player_action" in tree: state.player_action = tree["player_action"]
        if "player_remaining_action" in tree:
            state.player_remaining_action = tree["player_action"]

        card_saves = [CardSaveData(**save_obj) for save_obj in tree["deck"]]
        item_saves = [ItemSaveData(**save_obj) for save_obj in tree["inventory"]]
        return GameManager(state, tree["level_name"], card_saves, item_saves)

    def start_game(self):
        """초기화 메소드 직후에 호출되어 게임 시작 시의 로직을 수행."""
        if self.__game_state.current_turn == 0:
            self.__game_state.current_turn += 1
            self.__game_state.player_remaining_action = self.__game_state.player_action
            self.__game_state.player_attack = 0

            self.__event_manager.on_turn_begin(self.__game_state.current_turn)
            self.__event_manager.push_draw_event(DrawEvent(
                DrawEventType.TurnBegin,
                0, 0,
                self.__game_state.current_turn
            ))
            self.__event_manager.invoke_events(recursive=True)

    def save(self, path: str) -> None:
        """현재 게임 상태를 주어진 경로의 폴더에 저장."""
        # TODO: 저장 파일 포맷 완성
        self.__game_state.player_index = self.__deck.player_index
        tree: dict = {
            "level_name": self.__level_name,
            "datetime": datetime.now().strftime('%Y_%m_%d_%H_%M_%S'),
            "deck": [card.to_save_data().__dict__ for card in self.__deck.get_cards()],
            "inventory": [item.to_save_data().__dict__ for item in self.__inventory.get_items()],
            **self.__game_state.__dict__ # 나중에 고치시오
        }
        with open(
            os.path.join(path, f"{self.__level_name}_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.json"), 
            "w", encoding="utf-8") as f:
            json.dump(tree, f)

    def get_game_draw_state(self) -> GameDrawState:
        """현재 게임 상태를 반환. 주로 초기화에 사용."""
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
                card.is_front_face,
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

    def get_draw_events(self) -> List[DrawEvent | Tuple[CardDrawData, int] | ItemDrawData]:
        """이전 호출 이후로 생긴 게임 상태의 변화 등 이벤트의 목록을 반환."""
        return self.__event_manager.get_draw_event()

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
            "CardType": CardType,
            "get_card_data": cdm.get_card_data,
            "get_item_data": cdm.get_item_data,
            "player_index": self.__deck.player_index, 
            "abs": abs,
            "len": len
        }

    def get_writable_static_table(self, repeat = 1) -> Dict[str, Any]:
        """효과 스크립팅에서 사용 가능한 정적 변수/함수 목록 반환(쓰기 전용)."""

        def noop(*_, **__):
            pass

        if repeat <= 0:
            return {
            "modify_player_stat": noop,
            "add_item": noop,
            "end_turn": noop,
            "win_game": noop
            }

        return {
            "modify_player_stat": partial(self.modify_player_stat, repeat=repeat),
            "add_item": partial(self.add_item, repeat=repeat),
            "end_turn": self.end_turn,
            "win_game": self.win_game
        }
    
    def modify_player_stat(self, value_type: PlayerStat, amount: int, trigger_event:bool =False, repeat:int =1) -> None:
        """해당 플레이어 능력치를 amount만큼 변화."""
        if self.__game_end: return
        for _ in range(repeat):
            previous = 0
            current = 0
            match (value_type):
                case PlayerStat.Money:
                    previous = self.__game_state.player_money
                    self.__game_state.player_money = max(previous+amount, 0)
                    current = self.__game_state.player_money
                case PlayerStat.Health:
                    previous = self.__game_state.player_health
                    self.__game_state.player_health = max(previous+amount, 0)
                    current = self.__game_state.player_health
                case PlayerStat.Attack:
                    previous = self.__game_state.player_attack
                    self.__game_state.player_attack= max(previous+amount, 0)
                    current = self.__game_state.player_attack
                case PlayerStat.Action:
                    previous = self.__game_state.player_action
                    self.__game_state.player_action= max(previous+amount, 0)
                    current = self.__game_state.player_action
            if trigger_event:
                self.__event_manager.on_player_stat_changed(value_type, previous, current)
            self.__event_manager.push_draw_event(DrawEvent(
                DrawEventType.PlayerStatChanged,
                value_type.value,
                previous,
                current
            ))

    def after_action(self):
        """각 행동이 끝난 후 호출.
        비용 재계산, 패배 조건 검사, 카드 및 아이템 사용 가능 여부 계산 등의 작업 수행."""
        self.__event_manager.on_calculate_card_cost(True)
        self.__deck.apply_cost_modifier()
        if self.__game_state.player_health <= 0:
            self.lose_game(due_to_health=True)
            return
        lose = True
        for card in self.__deck.get_cards():
            if self.can_buy_card(card):
                lose = False
                break
        if lose:
            for item in self.__inventory.get_items():
                if self.can_use_item(item):
                    lose = False
                    break
        if lose:
            self.lose_game(due_to_health=False)

    def add_item(self, item_data: ItemData, amount: int = 1, repeat: int =1):
        """인벤토리에 아이템을 amount개만큼 추가."""
        if self.__game_end: return
        for _ in range(repeat):
            for i in range(amount):
                self.inventory.add_item(item_data)

    def can_buy_card(self, card: Optional[Card]) -> bool:
        """해당 id의 카드를 구매할 수 있는지 검사."""
        if self.__game_end or card is None: return False
        if not card.is_front_face: return False
        if card.card_data.type == CardType.Enemy:
            return self.__game_state.player_health + self.__game_state.player_attack >= card.modified_cost
        else:
            return self.__game_state.player_money >= card.modified_cost

    def buy_card(self, id: int) -> bool:
        """(가능하다면) 주어진 id의 카드를 구매함."""
        if self.__game_end or self.__game_state.player_remaining_action <= 0: return False
        card: Optional[Card] = self.__deck.get_card_by_id(id)
        if card is None or not self.can_buy_card(card): return False
        self.__event_manager.push_draw_event(DrawEvent(
            DrawEventType.CardPurchased,
            card.id,
            0, 0
        ))
        self.__game_state.player_remaining_action -= 1
        self.__event_manager.push_draw_event(DrawEvent(
            DrawEventType.PlayerStatChanged,
            PlayerStat.Action.value,
            self.__game_state.player_remaining_action+1, self.__game_state.player_remaining_action
        ))

        match (card.card_data.type):
            case CardType.Enemy:
                if self.__game_state.player_attack >= card.modified_cost:
                    previous: int = self.__game_state.player_attack
                    self.__game_state.player_attack -= card.modified_cost
                    self.__event_manager.on_player_stat_changed(
                        PlayerStat.Attack, 
                        previous,
                        previous - card.modified_cost
                    )
                    self.__event_manager.push_draw_event(DrawEvent(
                        DrawEventType.PlayerStatChanged,
                        PlayerStat.Attack.value,
                        previous, previous - card.modified_cost
                    ))
                else:
                    previous_atk = self.__game_state.player_attack
                    previous_health = self.__game_state.player_health
                    self.__game_state.player_health -= (card.modified_cost - self.__game_state.player_attack)
                    self.__game_state.player_attack = 0
                    self.__event_manager.on_player_stat_changed(
                        PlayerStat.Attack,
                        previous_atk, 0
                    )
                    self.__event_manager.push_draw_event(DrawEvent(
                        DrawEventType.PlayerStatChanged,
                        PlayerStat.Attack.value,
                        previous_atk, 0
                    ))
                    self.__event_manager.on_player_stat_changed(
                        PlayerStat.Health,
                        previous_health,
                        self.__game_state.player_health
                    )
                    self.__event_manager.push_draw_event(DrawEvent(
                        DrawEventType.PlayerStatChanged,
                        PlayerStat.Health.value,
                        previous_health, self.__game_state.player_health
                    ))
            case _:
                self.__game_state.player_money -= card.modified_cost
                self.__event_manager.push_draw_event(DrawEvent(
                    DrawEventType.PlayerStatChanged,
                    PlayerStat.Money.value,
                    self.__game_state.player_money+card.modified_cost, self.__game_state.player_money
                ))
        
        self.__event_manager.on_card_purchased(card)
        self.__event_manager.invoke_events(recursive=True)

        if self.__game_state.player_remaining_action <= 0:
            self.end_turn()

        self.after_action()

        return True

    def can_use_item(self, id: int) -> bool:
        """해당 id의 아이템을 사용할 수 있는지 검사."""
        if self.__game_end: return False
        items: List[Item] = self.__inventory.get_items(lambda x: x.id == id)
        if len(items) == 0:
            return False
        # item: Item = items[0]
        return True

    
    def use_item(self, id: int) -> bool:
        """(가능하다면) 주어진 id의 아이템을 사용함."""
        if self.__game_end or self.__game_state.player_remaining_action <= 0: return False
        item: Optional[Item] = self.__inventory.get_item_by_id(id)
        if item is None or not self.can_use_item(id): return False
        self.__game_state.player_remaining_action -= 1
        self.__event_manager.push_draw_event(DrawEvent(
            DrawEventType.ItemUsed,
            item.id,
            0, 0
        ))
        self.__event_manager.push_draw_event(DrawEvent(
            DrawEventType.PlayerStatChanged,
            PlayerStat.Action.value,
            self.__game_state.player_remaining_action+1, self.__game_state.player_remaining_action
        ))
        self.__event_manager.on_item_used(item)
        self.__event_manager.invoke_events(recursive=True)

        if self.__game_state.player_remaining_action <= 0:
            self.end_turn()

        self.after_action()

        return True

    # def can_end_turn(self) -> bool:
    #     """현재 턴을 넘길 수 있는 상태인지 검사."""
    
    def end_turn(self) -> None:
        """(가능하다면) 다음 턴으로 넘김."""
        if self.__game_end: return
        self.__event_manager.on_turn_end(self.__game_state.current_turn)
        self.__event_manager.push_draw_event(DrawEvent(
            DrawEventType.TurnEnd,
            0, 0,
            self.__game_state.current_turn
        ))
        self.__event_manager.invoke_events(recursive=True)

        self.__game_state.current_turn += 1
        prev_action = self.__game_state.player_remaining_action
        prev_attack = self.__game_state.player_attack
        self.__game_state.player_remaining_action = self.__game_state.player_action
        self.__game_state.player_attack = 0
        self.__event_manager.push_draw_event(DrawEvent(
            DrawEventType.TurnBegin,
            0, 0,
            self.__game_state.current_turn
        ))
        self.__event_manager.push_draw_event(DrawEvent(
            DrawEventType.PlayerStatChanged,
            PlayerStat.Action.value,
            prev_action, self.__game_state.player_action
        ))
        self.__event_manager.push_draw_event(DrawEvent(
            DrawEventType.PlayerStatChanged,
            PlayerStat.Attack.value,
            prev_attack, 0
        ))

        self.__event_manager.on_turn_begin(self.__game_state.current_turn)
        self.__event_manager.invoke_events(recursive=True)

    def win_game(self) -> None:
        """게임을 승리한 것으로 처리."""
        self.__event_manager.push_draw_event(DrawEvent(
            DrawEventType.PlayerWon,
            0, 0, 0
        ))
        self.__game_end = True

    def lose_game(self, due_to_health: bool) -> None:
        """게임을 패배한 것으로 처리.
        due_to_health: 참 - 체력에 의한 패배, 거짓 - 행동 불능에 의한 패배."""
        self.__event_manager.push_draw_event(DrawEvent(
            DrawEventType.PlayerLost,
            (0 if due_to_health else 1), 0, 0
        ))
        self.__game_end = True
    