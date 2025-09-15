from textual.screen import Screen
from textual.widgets import Input, TextArea, Static, ListItem, ListView, Header, Footer
from textual.containers import HorizontalScroll, VerticalScroll, Container
from textual.events import Key
from textual.timer import Timer
from database import Banco
from controller import Controller
import time


class TelaInicial(Screen):
    CSS_PATH = "css/TelaInicial.tcss"
    nome_user = ""
    users = dict()
    mensagens = []
    _poll_timer: Timer = None
    imagens = dict()

    def compose(self):
        yield Header()
        with HorizontalScroll():
            with VerticalScroll():
                yield TextArea(read_only=True)
                yield Input(placeholder="Digite aqui")
            yield VerticalScroll(id="vs_imagens")
            yield ListView(id="lv_usuarios")
        yield Footer()

    def on_key(self, event: Key):
        if event.key == "enter" and self.nome_user:
            input_widget = self.query_one(Input)
            if input_widget.value:
                if "//" in input_widget.value or "\\" in input_widget.value:
                    imagem_gerada = Controller.resize(input_widget.value)
                    if imagem_gerada:
                        pixel = Controller.gerar_pixel(imagem_gerada)
                        if pixel:
                            imagem_static = Static(pixel)
                            self.query_one(
                                "#vs_imagens", VerticalScroll).styles.width = "20%"
                            self.query_one("#vs_imagens", VerticalScroll).mount(
                                Static(f"{self.nome_user}:"))
                            self.query_one("#vs_imagens", VerticalScroll).mount(
                                imagem_static)
                            self.imagens[self.nome_user] = pixel
                            Banco.salvar("banco.db", "imagens", self.imagens)
                        else:
                            self.notify("ERRO com a imagem!")
                    else:
                        self.notify("ERRO com a imagem!")
                else:
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

        carregar_imagens = Banco.carregar("banco.db", "imagens")
        if carregar_imagens:
            self.query_one(
                "#vs_imagens", VerticalScroll).styles.width = "20%"
            for usuario, imagem in carregar_imagens.items():
                self.query_one("#vs_imagens", VerticalScroll).mount(
                    Static(f"{usuario}:"))
                self.query_one("#vs_imagens", VerticalScroll).mount(
                    Static(imagem))

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
