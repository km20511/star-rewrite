from typing import List

import pyglet

from gui.scenes import IntroScene, MainScene

FONTS_PATH: str = "data/fonts"


def main() -> None:

    pyglet.font.add_directory(FONTS_PATH)

    app_window = pyglet.window.Window(caption="Star Rewrite", resizable=True)
    # app_window.set_fullscreen(True)

    intro_scene = IntroScene(app_window)
    main_scene = MainScene(app_window)

    intro_scene.load(lambda path: (intro_scene.unload(), main_scene.load(path)))
    
    pyglet.app.run()


if __name__ == '__main__':
    main()