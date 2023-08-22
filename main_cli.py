import os
import cmd
import sys
import json
from pprint import pprint
from functools import reduce
from datetime import datetime
from typing import IO, Dict, Final, List, Literal

from core import GameManager
from core.enums import CardType, DrawEventType, PlayerStat
from core.obj_data_formats import CardDrawData, DrawEvent, ItemDrawData

LEVEL_PATH: Final[str] = "data/levels"
SAVES_PATH: Final[str] = "data/saves"

CARDTYPE_REPR: Final[Dict[CardType, str]] = {
    CardType.Enemy: "적",
    CardType.Item: "아이템",
    CardType.Event: "사건"
}

def select_input(
        question: str,
        options: List[str],
        prompt: str = "> ",
        on_invalid: str = "주어진 선택지 또는 해당 번호 중 하나를 입력하세요.",
        print_option: bool = True,
        allow_key: bool = True,
        allow_value: bool = True,
        allow_exit: bool = True
        ) -> int:
    """주어진 질문에 대한 유효한 답을 얻을 때까지 질문을 반복.
    주의: 반환값은 0부터의 인덱스. 출력된 번호보다 1 작음.
    options가 비어 있거나 빈문자열을 포함하면 -1 반환.
    allow_exit이 True일 때 exit 또는 quit이 입력되면 -2 반환."""
    answer: str = ""

    if not (allow_key or allow_value) or  len(options) == 0 or "" in options: 
        return -1

    if question != "":
        print(question)

    if print_option:
        for num, option in enumerate(options):
            print(f" {num+1}) {option}")

    while True:
        answer = input(prompt)
        if allow_exit and answer.strip().lower() in ("quit", "exit"):
            return -2
        if allow_value and answer in options:
            return options.index(answer)
        if allow_key and answer.isdigit() and 1 <= int(answer) <= len(options):
            return int(answer) - 1
        print(on_invalid)

def align_korean(
        text: str, 
        total_length: int, 
        align: Literal["l", "c", "r"] = "l", 
        fill: str = " "
    ):
    """한글의 글자폭을 2칸으로 계산해 터미널에서 정렬이 맞도록 함.
    주의: total_length가 계산된 길이보다 짧으면 입력 문자열 그대로 반환.
    주의: fill 문자 및 한글 이외의 문자는 1칸으로 전제함."""
    length: int = reduce(lambda a, b: (a+2 if '가' <= b <= '힣' else a+1), text, 0)
    if length >= total_length: 
        return text
    num_fill: int = total_length - length
    match (align):
        case "l":
            return text + fill*num_fill
        case "r":
            return fill*num_fill + text
        case "c":
            return fill*(num_fill//2) + text + fill*(num_fill-num_fill//2)

class Shell(cmd.Cmd):
    """CLI 게임을 진행하는 셸."""
    
    prompt: str = "(명령을 입력하세요): "

    def __init__(self, completekey: str = "tab", stdin: IO[str] | None = None, stdout: IO[str] | None = None) -> None:
        print(
            "Star Rewrite CLI에 오신 것을 환영합니다!"
            "help 또는 ?를 입력하면 도움말을 볼 수 있습니다."
            "아래 목록에서 시작할 게임을 선택하세요."
        )

        levels: List[str] = [i for i in os.listdir(LEVEL_PATH) if i.endswith(".json")]
        saves: List[str] = [i for i in os.listdir(SAVES_PATH) if i.endswith(".json")]

        if len(levels) + len(saves) == 0:
            print(
                "사용 가능한 파일이 없습니다. 아래 폴더에 최소 하나 이상의 json이 필요합니다.",
                LEVEL_PATH, SAVES_PATH, sep="\n")
            sys.exit()

        option_list: List[str] = ["" for _ in range(len(levels) + len(saves))]
        level_names: List[str] = option_list.copy()
        option_index: int = 0

        print("="*20)
        print("새 게임 생성:")
        for filename in levels:
            with open(os.path.join(LEVEL_PATH, filename), encoding="utf-8") as f:
                tree: dict = json.load(f)
            level_name: str = tree["level_name"]
            print(f" {option_index + 1}) {level_name}")
            option_list[option_index] = filename
            level_names[option_index] = level_name
            option_index += 1
        
        print("="*20)
        print("이전 기록 불러오기:")
        for filename in saves:
            with open(os.path.join(SAVES_PATH, filename), encoding="utf-8") as f:
                tree = json.load(f)
            level_name = tree["level_name"]
            date: str = (datetime.strptime(tree["datetime"], "%Y_%m_%d_%H_%M_%S")
                            .strftime("%Y/%m/%d %H:%M:%S")
                            if "datetime" in tree else "----/--/-- --:--:--")
            print(f" {option_index + 1}) {filename}\t{level_name}\t{date}")
            option_list[option_index] = filename
            level_names[option_index] = level_name
            option_index += 1
        print("="*20)

        selected: int = select_input("", option_list, print_option=False, allow_value=False)
        if selected == -2:
            print("프로그램을 종료합니다.")
            sys.exit()

        self.game = GameManager.create_from_file(
            os.path.join(
                LEVEL_PATH if selected < len(levels) else SAVES_PATH, option_list[selected]
            )
        )
        self.game_state = self.game.get_game_draw_state()
        self.level_name = level_names[selected]

        print("게임을 시작합니다.")
        self.process_draw_events()
        
        super().__init__(completekey, stdin, stdout)

    def do_state(self, args):
        """현재 게임 상태를 출력합니다(디버그용)."""
        self.game_state = self.game.get_game_draw_state()
        print(
            f"======== 게임 정보 ========\n"
            f"이야기 : {self.level_name}\t\t{self.game_state.current_turn} 턴\n"
            f"======== 플레이어 ========\n"
            f"돈: {self.game_state.player_money}\t 체력: {self.game_state.player_health}\t"
            f"공격력: {self.game_state.player_attack}\t 행동: {self.game_state.player_remaining_action}"
        )
        # pprint(self.game_state)

    def do_deck(self, args: str):
        """현재 덱을 출력합니다.
        --debug 옵션으로 앞면 여부에 상관없이 카드를 볼 수 있습니다."""
        result: str = "(순번, 이름, 유형, 비용)\n"
        debug: bool = "--debug" in args
        for ind, card in enumerate(self.game_state.deck):
            result += (f"{ind:>2d}) "
                       f"""{align_korean(card.name, 30) 
                            if debug or card.is_front_face 
                            else '???'+' '*27}\t"""
                       f"{align_korean(CARDTYPE_REPR[card.type], 6, align='r')}\t"
                       f"""{(f'*{card.current_cost}*' 
                            if card.current_cost != card.base_cost
                            else f'{card.current_cost}')
                            if debug or card.is_front_face else '???':>4s}\n"""
                    )
        print(result)

    def do_inventory(self, args) -> None:
        """현재 인벤토리를 출력합니다."""
        if len(self.game_state.inventory) == 0:
            print("보유한 아이템이 없습니다.")
            return
        result: str = "(순번, 이름)\n"
        for ind, item in enumerate(self.game_state.inventory):
            result += (f"{ind:>2d}) {align_korean(item.name, 30)}")
    
    def do_card(self, args: str) -> None:
        """해당 번호의 카드 정보를 봅니다."""
        if not (args.isdigit() and 0 <= int(args) < len(self.game_state.deck)):
            print("덱 카드의 번호 중 하나를 입력하세요.")
            return
        card = self.game_state.deck[int(args)]
        if not card.is_front_face:
            print("이 운명은 아직 알 수 없습니다.")
            return
        print(
            "======== 카드 정보 ========\n"
            f"이름: {card.name}\n"
            f"기본 비용: {card.base_cost}\t현재 비용: {card.current_cost}\n"
            f"유형: {CARDTYPE_REPR[card.type]}\n"
            f"{card.description}\n"
            "========================="
        )


    def do_buy(self, args: str):
        """주어진 번호의 카드를 구매합니다."""
        if not (args.isdigit() and 0 <= int(args) < len(self.game_state.deck)):
            print("덱 카드의 번호 중 하나를 입력하세요.")
            return
        self.game.buy_card(self.game_state.deck[int(args)].id)
        self.process_draw_events()

    def do_drawevents(self, args):
        """현재 처리하지 않은 DrawEvent들을 출력합니다(디버그용)."""
        pprint(self.game.get_draw_events())

    def do_exit(self, args):
        """프로그램을 종료합니다."""
        return True

    do_quit = do_exit

    def _search_card_by_id(self, id: int):
        """현재 게임 상태에서 id로 카드 데이터를 검사."""
        for card in self.game_state.deck:
            if card.id == id:
                return card
        return None

    def _search_item_by_id(self, id: int):
        """현재 게임 상태에서 id로 아이템 데이터를 검사."""
        for item in self.game_state.inventory:
            if item.id == id:
                return item
        return None

    def process_draw_events(self) -> bool:
        """처리하지 않은 DrawEvent를 처리."""
        events = self.game.get_draw_events()
        while len(events) > 0:
            event = events.pop(0)
            if isinstance(event, DrawEvent):
                match (event.event_type):
                    case DrawEventType.TurnBegin:
                        print(f"{event.current}번째 턴입니다.")
                        self.game_state.current_turn = event.current
                    case DrawEventType.TurnEnd:
                        pass
                    case DrawEventType.CardCreated:
                        pass # DrawEvent가 아닌 (CardDrawData, int)가 들어오는 경우 처리.
                    case DrawEventType.CardShown:
                        card = self._search_card_by_id(event.target_id)
                        if card is not None:
                            card.is_front_face = bool(event.current)
                            if event.current:
                                print(f"카드 공개됨: {card.name}")
                    case DrawEventType.CardMoved:
                        moved_events = [event]
                        while len(events) > 0 and isinstance(events[0], DrawEvent) and events[0].event_type == DrawEventType.CardMoved:
                            moved_events.append(events[0])
                            events.pop(0)

                        new_card_list: List[CardDrawData | None] = [None for _ in range(len(self.game_state.deck))]
                        for index, card in enumerate(self.game_state.deck):
                            for moved_event in moved_events:
                                if card.id == moved_event.target_id:
                                    new_card_list[moved_event.current] = card
                                    break
                            else:
                                new_card_list[index] = card
                        self.game_state.deck = [card for card in new_card_list if card is not None]
                    case DrawEventType.CardPurchased:
                        print(f"카드를 구매했습니다: {self._search_card_by_id(event.target_id).name}")
                    case DrawEventType.CardDestroyed:
                        card = self._search_card_by_id(event.target_id)
                        if card is not None:
                            self.game_state.deck.remove(card)
                    case DrawEventType.CardCostChanged:
                        raise NotImplementedError
                    case DrawEventType.ItemCreated:
                        pass # DrawEvent가 아닌 ItemDrawData가 들어오는 경우 처리.
                    case DrawEventType.ItemUsed:
                        print(f"아이템을 사용했습니다: {self._search_item_by_id(event.target_id)}")
                    case DrawEventType.ItemDestroyed:
                        item = self._search_item_by_id(event.target_id)
                        if item is not None:
                            self.game_state.inventory.remove(item)
                    case DrawEventType.PlayerWon:
                        print("승리! 목적을 달성했습니다!")
                        return True
                    case DrawEventType.PlayerLost:
                        print("패배! some text goes here.")
                        return True
                    case DrawEventType.PlayerStatChanged:
                        # match (PlayerStat(event.target_id)):
                        #     case PlayerStat.Money:
                        delta: int = event.current - event.previous
                        print(
                            f"수치 변화: {PlayerStat(event.target_id).name},"
                            f" {event.previous} -> {event.current}"
                            f" ({'+' if delta > 0 else '-'}{abs(delta)})"
                        )
            elif isinstance(event, ItemDrawData):
                # 아이템 생성 이벤트.
                print(f"아이템 생성됨: {event.name}")
                self.game_state.inventory.append(event)
            else:
                # Tuple[CardDrawData, int]. 카드 생성 이벤트.
                print(f"카드 생성됨: {event[0].name}")
                self.game_state.deck.insert(event[1], event[0])
        return False


if __name__ == "__main__":
    Shell().cmdloop()