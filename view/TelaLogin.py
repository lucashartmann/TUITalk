from textual.screen import Screen
from textual.widgets import Static,  Button, Header, Footer, TextArea
from textual.color import Color
from database.Banco import Banco
from view.TelaInicial import TelaInicial
import time
from textual_colorpicker import ColorPicker
from textual.containers import Center
from model import Usuario


class TelaLogin(Screen):

    CSS_PATH = "css/TelaLogin.tcss"
    bd = Banco()

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


    def on_button_pressed(self):
        carregar_users = self.bd.carregar_usuarios() or list()
        nome_input = self.query_one("#usuario", TextArea).text
        cor = self.query_one(ColorPicker).color
        agora = int(time.time())

        if cor:
            for user in carregar_users:
                last_seen = user.get_tempo()
                if user.get_cor() == cor.hex and agora - last_seen <= 60:
                    self.notify("ERRO! Cor já escolhida")
                    return
            

        if not nome_input:
            self.notify("ERRO! Valor inválido")
            return

        user = Usuario.Usuario()
        user.set_nome(nome_input)
        if isinstance(cor, Color):
            user.set_cor(cor.hex)
        else:
            user.set_cor(cor)
        user.set_tempo(agora)

        TelaInicial.usuario = user
        
        #TODO: se agora - last_seen <= 60 substitui o usuário
        self.bd.salvar_usuario(user) 

        self.app.switch_screen("tela_inicial")
