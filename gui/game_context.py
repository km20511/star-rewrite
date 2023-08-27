from typing import Callable


class GameContext:
    """모든 Scene이 공유하는 게임 상태.
    Scene을 관리하고 있는 스크립트에서 생성해 사용."""
    def __init__(self, on_change_scene: Callable[[str], None], file_path: str = "") -> None:
        self.on_change_scene = on_change_scene
        self.file_path: str = file_path
    
    def load_scene(self, name: str):
        """주어진 이름으로 Scene을 불러오게 함."""
        self.on_change_scene(name)

    