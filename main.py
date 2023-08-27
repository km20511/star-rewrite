from typing import Dict, List, Optional

import pyglet

from gui.game_context import GameContext
from gui.scenes import IntroScene, MainScene, Scene

FONTS_PATH: str = "data/fonts"


def main() -> None:

    pyglet.font.add_directory(FONTS_PATH)
    pyglet.resource.path = ["data/fonts", "data/images/game_sprites"]
    pyglet.resource.reindex()

    app_window = pyglet.window.Window(caption="Star Rewrite", resizable=True)

    scenes: Dict[str, Scene] = {}
    current_scene: Optional[Scene] = None

    def load_scene(name: str):
        nonlocal scenes, current_scene
        assert name in scenes, f"'{name}'의 이름을 가진 Scene은 등록되지 않았습니다."
        if current_scene is not None: current_scene.unload()
        current_scene = scenes[name]
        current_scene.load()

    game_context = GameContext(on_change_scene=load_scene)
    # app_window.set_fullscreen(True)

    scenes["intro"] = IntroScene(app_window, game_context)
    scenes["main"] = MainScene(app_window, game_context)

    # intro_scene.load(lambda path: (intro_scene.unload(), main_scene.load(path)))
    game_context.file_path = "data/levels/tutorial_0.json"
    load_scene("main")
    
    pyglet.app.run()


if __name__ == '__main__':
    main()