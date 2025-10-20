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

        user = Usuario.Usuario()

        ja_existe = False
        susbtituir = False

        if cor:
            for usuario in carregar_users:
                last_seen = usuario.get_tempo()
                if usuario.get_cor() == cor.hex and agora - last_seen <= 60:
                    self.notify("ERRO! Cor já escolhida")
                    ja_existe = True
                    break
                elif usuario.get_cor() == cor.hex and agora - last_seen > 60:
                    user = usuario
                    susbtituir = True
                    break

        if not nome_input:
            self.notify("ERRO! Valor inválido")
            return

        if not ja_existe:
            user.set_nome(nome_input)
            if isinstance(cor, Color):
                user.set_cor(cor.hex)
            else:
                user.set_cor(cor)
            user.set_foto("")
            user.set_tempo(agora)

            TelaInicial.usuario = user

            if susbtituir:
                self.bd.atualizar("Usuario", "foto", "cor",
                                  user.get_foto(), cor.hex)
                self.bd.atualizar("Usuario", "status", "cor",
                                  user.get_status(), cor.hex)
                self.bd.atualizar("Usuario", "nome", "cor",
                                  user.get_nome(), cor.hex)
                self.bd.atualizar("Usuario", "tempo", "cor",
                                  user.get_tempo(), cor.hex)
            else:
                self.bd.salvar_usuario(user)

            self.app.switch_screen("tela_inicial")