import os
import cmd
import sys
import json
from pprint import pprint
from datetime import datetime
from typing import IO, Final, List

from core import GameManager

LEVEL_PATH: Final[str] = "data/levels"
SAVES_PATH: Final[str] = "data/saves"

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
        if answer.strip().lower() in ("quit", "exit"):
            return -2
        if allow_value and answer in options:
            return options.index(answer)
        if allow_key and answer.isdigit() and 1 <= int(answer) <= len(options):
            return int(answer) - 1
        print(on_invalid)


class Shell(cmd.Cmd):
    """CLI 게임을 진행하는 셸."""
    
    prompt: str = "(명령을 입력하세요): "

    def __init__(self, completekey: str = "tab", stdin: IO[str] | None = None, stdout: IO[str] | None = None) -> None:
        print(f"""\
Star Rewrite CLI에 오신 것을 환영합니다!
help 또는 ?를 입력하면 도움말을 볼 수 있습니다.
아래 목록에서 시작할 게임을 선택하세요.""")

        levels: List[str] = [i for i in os.listdir(LEVEL_PATH) if i.endswith(".json")]
        saves: List[str] = [i for i in os.listdir(SAVES_PATH) if i.endswith(".json")]

        if len(levels) + len(saves) == 0:
            print(f"""사용 가능한 파일이 없습니다. 아래 폴더에 최소 하나 이상의 json이 필요합니다.
{LEVEL_PATH}
{SAVES_PATH}""")
            sys.exit()

        option_list: List[str] = ["" for _ in range(len(levels) + len(saves))]
        option_index: int = 0

        print("="*20)
        print("새 게임 생성:")
        for filename in levels:
            with open(os.path.join(LEVEL_PATH, filename), encoding="utf-8") as f:
                tree: dict = json.load(f)
            level_name: str = tree["level_name"]
            print(f" {option_index + 1}) {level_name}")
            option_list[option_index] = filename
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
        
        super().__init__(completekey, stdin, stdout)

    def do_state(self, args):
        """현재 게임 상태를 출력합니다(디버그용)."""
        pprint(self.game.get_game_draw_state())

    def do_drawevents(self, args):
        """현재 처리하지 않은 DrawEvent들을 출력합니다(디버그용)."""
        pprint(self.game.get_draw_events())

    def do_exit(self, args):
        """프로그램을 종료합니다."""
        return True

    do_quit = do_exit


if __name__ == "__main__":
    Shell().cmdloop()