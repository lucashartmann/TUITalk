from textual.app import App
from view import TelaInicial, TelaLogin


class App(App):

    SCREENS = {
        "tela_login": TelaLogin.TelaLogin,
        "tela_inicial": TelaInicial.TelaInicial
    }

    def on_mount(self):
        self.push_screen("tela_login")
