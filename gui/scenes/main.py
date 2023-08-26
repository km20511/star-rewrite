from gui.scenes import Scene

class MainScene(Scene):
    def load(self, filepath: str):
        super().load()
        @self.window.event
        def on_draw():
            self.window.clear()