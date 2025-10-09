from textual.app import App
from view import TelaInicial, TelaLogin, TelaServidor
from database import Banco

class App(App):
    
    

    SCREENS = {
        "tela_login": TelaLogin.TelaLogin,
        "tela_inicial": TelaInicial.TelaInicial,
        "tela_servidor": TelaServidor.TelaServidor
    }
    
    tela = "tela_login"
    servidor = False

    def on_mount(self):
            self.push_screen(self.tela)
