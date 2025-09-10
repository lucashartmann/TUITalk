from textual.app import App
from view import TelaInicial

class App(App):
    
    SCREENS = {
        "tela_inicial": TelaInicial.TelaInicial
    }
    
    
    def on_mount(self):
        self.push_screen("tela_inicial")
        
        