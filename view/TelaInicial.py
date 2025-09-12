from textual.screen import Screen
from textual.widgets import Input, TextArea, Static, ListItem, ListView, Header, Footer
from textual.containers import HorizontalScroll, VerticalScroll
from textual.events import Key
from textual.timer import Timer
from database import Banco
import time


class TelaInicial(Screen):
    CSS_PATH = "css/TelaInicial.tcss"
    nome_user = ""
    users = dict()
    mensagens = []
    _poll_timer: Timer = None

    def compose(self):
        yield Header()
        with HorizontalScroll():
            with VerticalScroll():
                yield TextArea(read_only=True)  # read-only = True
                yield Input(placeholder="Digite aqui")
            yield ListView(id="lv_usuarios")
        yield Footer()

    def on_key(self, event: Key):
        if event.key == "enter" and self.nome_user:
            input_widget = self.query_one(Input)
            if input_widget.value:
                nova_mensagem = f"{self.nome_user}\n  {input_widget.value}\n"
                self.mensagens.append(nova_mensagem)
                Banco.salvar("banco.db", "mensagens", self.mensagens)
                self.query_one(TextArea).text += nova_mensagem
                input_widget.clear()

    def on_mount(self):
        users = self.listar_usuarios()
        self.atualizar_lista_users(users)

        carregar_users = Banco.carregar("banco.db", "usuarios")
        if carregar_users:
            self.users = carregar_users
        carregar_msgs = Banco.carregar("banco.db", "mensagens")
        if carregar_msgs:
            self.mensagens = carregar_msgs
            self.query_one(TextArea).text = "".join(self.mensagens)

        self._poll_timer = self.set_interval(2, self.poll_dados)

    def poll_dados(self):
        if self.nome_user != "":
            self.atualizar_usuario()
            users = self.listar_usuarios()

            carregar_users = Banco.carregar("banco.db", "usuarios")
            if carregar_users and carregar_users != self.users:
                self.users = carregar_users
                self.atualizar_lista_users(users)

            carregar_msgs = Banco.carregar("banco.db", "mensagens")
            if carregar_msgs and carregar_msgs != self.mensagens:
                self.mensagens = carregar_msgs
                self.query_one(TextArea).text = "".join(self.mensagens)

    def listar_usuarios(self):
        if self.nome_user != "":
            agora = int(time.time())
            usuarios = Banco.carregar("banco.db", "usuarios")
            ativos = {}
            for chave, valor in usuarios.items():
                if agora - valor <= 60:
                    ativos[f"🟢 {chave}"] = valor
                else:
                    ativos[f"🔴 {chave}"] = valor
            return ativos

    def atualizar_usuario(self):
        agora = int(time.time())
        usuarios = Banco.carregar("banco.db", "usuarios") or {}
        usuarios[self.nome_user] = agora
        Banco.salvar("banco.db", "usuarios", usuarios)
        self.users = self.listar_usuarios()

    def atualizar_lista_users(self, users):
        lista = self.query_one("#lv_usuarios", ListView)
        lista.remove_children()
        if users:
            for user in users.keys():
                lista.append(ListItem(Static(user)))
