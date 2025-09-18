from textual.app import App
from textual.widgets import TextArea, Button, Static
from controller import Controller

class App(App):
    def compose(self):
        yield TextArea()
        
    def on_mount(self):
        imagem = Controller.resize("assets/download.png")
        pixel = Controller.gerar_pixel(imagem)
        self.query_one(TextArea).mount(Static(("lucas", pixel)))
        
App().run()
        