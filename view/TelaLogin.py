from textual.screen import Screen
from textual.widgets import Input, Static,  Button, Header, Footer
from database import Banco
from view.TelaInicial import TelaInicial
import time


class TelaLogin(Screen):

    CSS_PATH = "css/TelaLogin.tcss"

    def compose(self):
        yield Header()
        yield Static("Ｌｏｇｉｎ", id="titulo")
        yield Static("Nome")
        yield Input(placeholder="Nome aqui", id="usuario")
        yield Button("Entrar")
        yield Footer()

    nome = ""

    def on_button_pressed(self):
        carregar_users = Banco.carregar("banco.db", "usuarios") or {}
        TelaInicial.users = carregar_users
        valor_input = self.query_one("#usuario", Input).value.strip()

        if not valor_input:
            self.notify("ERRO! Valor inválido")
            return

        agora = int(time.time())

        if valor_input in TelaInicial.users:
            last_seen = TelaInicial.users[valor_input]

            if agora - last_seen <= 60:
                self.notify("ERRO! Nome já em uso")
                return
            else:
                TelaInicial.nome_user = valor_input
                TelaInicial.users[valor_input] = agora

        else:
            TelaInicial.nome_user = valor_input
            TelaInicial.users[TelaInicial.nome_user] = agora

        Banco.salvar("banco.db", "usuarios", TelaInicial.users)

        self.app.switch_screen("tela_inicial")
