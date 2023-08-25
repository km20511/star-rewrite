from typing import List

import pyglet

from gui.scenes import Scene, IntroScene

FONTS_PATH: str = "data/fonts"

def main() -> None:

    pyglet.font.add_directory(FONTS_PATH)

    app_window = pyglet.window.Window(caption="Star Rewrite", resizable=True)
    # app_window.set_fullscreen(True)

    scenes: List[Scene] = [
        IntroScene(app_window)
    ]
    scenes[0].load()
    
    pyglet.app.run()


if __name__ == '__main__':
    main()