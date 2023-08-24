import pyglet


def main():
    res_w: int = 1280
    res_h: int = 720

    app_window = pyglet.window.Window(res_w, res_h, caption="Star Rewrite")
    
    pyglet.app.run()


if __name__ == '__main__':
    main()