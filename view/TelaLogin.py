from textual.screen import Screen
from textual.widgets import Static,  Button, Header, Footer, TextArea
from textual.color import Color
from database import Banco
from view.TelaInicial import TelaInicial
import time
from textual_colorpicker import ColorPicker
from textual.containers import Center
from model import Usuario


class TelaLogin(Screen):

    CSS_PATH = "css/TelaLogin.tcss"

    def compose(self):
        yield Header()
        with Center():
            yield Static("Nome:")
        with Center():
            yield TextArea(placeholder="Nome aqui", id="usuario")
        with Center():
            yield Static("Cor do nome:")
        with Center():
            yield ColorPicker()
        with Center():
            yield Button("Entrar")
        yield Footer()

    nome = ""
    
    # @on(ColorPicker.Changed)
    # def cor_mudou(self, evento = ColorPicker.Changed):
    #     self.notify(str(self.query_one(ColorPicker).color))


    def on_button_pressed(self):
        carregar_users = Banco.carregar("banco.db", "usuarios") or {}
        nome_input = self.query_one("#usuario", TextArea).text
        cor = self.query_one(ColorPicker).color
        agora = int(time.time())

        # Verifica se a cor já está em uso recentemente
        if cor:
            for user in carregar_users.values():
                last_seen = user.get_tempo()
                if user.get_cor() == cor and agora - last_seen <= 60:
                    self.notify("ERRO! Cor já escolhida")
                    return
            try:
                Color.parse(cor)
            except Exception:
                self.notify("ERRO! Cor inválida")
                return

        if not nome_input:
            self.notify("ERRO! Valor inválido")
            return

        user = Usuario.Usuario()
        user.set_nome(nome_input)
        user.set_cor(cor)
        user.set_tempo(agora)

        carregar_users[nome_input] = user
        self.app.usuario_logado = user
        Banco.salvar("banco.db", "usuarios", carregar_users)

        self.app.switch_screen("tela_inicial")
