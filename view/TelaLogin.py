from textual.screen import Screen
from textual.widgets import Input, Static,  Button, Header, Footer
from database import Banco
from view.TelaInicial import TelaInicial
import time
from unidecode import unidecode


class TelaLogin(Screen):

    CSS_PATH = "css/TelaLogin.tcss"

    def compose(self):
        yield Header()
        yield Static("Nome:")
        yield Input(placeholder="Nome aqui", id="usuario")
        yield Static("Cor do nome:")
        yield Input(placeholder="Cor aqui", id="cor")
        yield Button("Entrar")
        yield Footer()

    nome = ""

    def on_button_pressed(self):
        carregar_users = Banco.carregar("banco.db", "usuarios") or {}
        TelaInicial.users = carregar_users
        nome_input = self.query_one("#usuario", Input).value.strip()
        cor = unidecode(self.query_one("#cor", Input).value.strip().lower())

        if not nome_input:
            self.notify("ERRO! Valor inválido")
            return

        agora = int(time.time())

        if nome_input in TelaInicial.users:
            last_seen = TelaInicial.users[nome_input]

            if agora - last_seen <= 60:
                self.notify("ERRO! Nome já em uso")
                return
            else:
                user = TelaInicial.usuario
                user.set_nome(nome_input)
                user.set_cor(cor)
                user.set_tempo(agora)
                TelaInicial.users[user.get_nome()] = user

        else:
            user = TelaInicial.usuario
            user.set_nome(nome_input)
            user.set_cor(cor)
            user.set_tempo(agora)
            TelaInicial.users[user.get_nome()] = user

        Banco.salvar("banco.db", "usuarios", TelaInicial.users)

        self.app.switch_screen("tela_inicial")
