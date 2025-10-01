from textual.screen import Screen
from textual.widgets import Input, Static,  Button, Header, Footer
from textual.color import Color
from database import Banco
from view.TelaInicial import TelaInicial
import time
from textual_colorpicker import ColorPicker

class TelaLogin(Screen):

    CSS_PATH = "css/TelaLogin.tcss"

    def compose(self):
        yield Header()
        yield Static("Nome:")
        yield Input(placeholder="Nome aqui", id="usuario")
        yield Static("Cor do nome:")
        yield ColorPicker()
        yield Button("Entrar")
        yield Footer()

    nome = ""
    
    # @on(ColorPicker.Changed)
    # def cor_mudou(self, evento = ColorPicker.Changed):
    #     self.notify(str(self.query_one(ColorPicker).color))


    def on_button_pressed(self):
        carregar_users = Banco.carregar("banco.db", "usuarios") or {}
        nome_input = self.query_one("#usuario", Input).value.strip()

        cor = self.query_one(ColorPicker).color

        if carregar_users and cor:
                for user in carregar_users.values():
                    last_seen = user.get_tempo()
                    if user.get_cor() == cor and agora - last_seen <= 60:
                        self.notify("ERRO! Cor já escolhida")
                        return

        if cor:
            try:
                Color.parse(cor)
            except Exception:
                self.notify("ERRO! Cor inválida")
                return

        if not nome_input:
            self.notify("ERRO! Valor inválido")
            return

        agora = int(time.time())

        
        if carregar_users and nome_input in carregar_users.keys():
            last_seen = carregar_users[nome_input].get_tempo()

            if agora - last_seen <= 60:
                self.notify("ERRO! Nome já em uso")
                return
            else:
                user = TelaInicial.usuario
                user.set_nome(nome_input)
                user.set_cor(cor)
                user.set_tempo(agora)
                carregar_users[user.get_nome()] = user

        else:
            user = TelaInicial.usuario
            user.set_nome(nome_input)
            user.set_cor(cor)
            user.set_tempo(agora)
            carregar_users[user.get_nome()] = user

        Banco.salvar("banco.db", "usuarios", carregar_users)

        self.app.switch_screen("tela_inicial")
