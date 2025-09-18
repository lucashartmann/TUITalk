from textual.screen import Screen
from textual.widgets import Input, TextArea, Static, ListItem, ListView, Header, Button, Footer
from textual.containers import HorizontalScroll, VerticalScroll, HorizontalGroup
from textual.events import Key
from textual.timer import Timer
from database import Banco
from controller import Controller
import time
from model import Audio
import wave
from textual.events import Click


class TelaInicial(Screen):
    CSS_PATH = "css/TelaInicial.tcss"
    nome_user = ""
    users = dict()
    mensagens = list()
    _poll_timer: Timer = None
    audio = Audio.ChatVoz()
    audios = dict()

    def compose(self):
        yield Header()
        with HorizontalScroll():
            with VerticalScroll():
                yield TextArea(read_only=True)
                with HorizontalGroup():
                    yield Input(placeholder="Digite aqui")
                    yield Button("🔴", id="gravar")
                    # yield Button("▶️", id="play")
            yield ListView(id="lv_usuarios")
        yield Footer()

    def on_click(self, evento: Click):
        if isinstance(evento.widget, Static):
            self.notify("Clicado")
            if "▶︎" in evento.widget.content:
                arquivo = self.audios[evento.widget.name]
                self.audio.tocar_audio(arquivo)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "gravar":
            if not self.audio.is_recording:
                self.query_one(Button).label = "⬛"
                self.query_one(Input).disabled = True
                self.query_one(Input).value = "▶• Recording..."
                self.audio.start_recording()
            else:
                self.query_one(Button).label = "🔴"
                self.query_one(Input).disabled = False
                self.query_one(Input).value = ""
                self.audio.stop_recording()
                arquivo = wave.open("mensagem.wav", "rb")
                nova_mensagem = Static(
                    f"{self.nome_user}\n  ▶︎ •၊၊||၊|။||||။‌‌‌‌‌၊|• \n", name=hash(arquivo))
                self.audios[nova_mensagem.name] = arquivo
                self.mensagens.append(
                    {"autor": self.nome_user, "mensagem": "▶︎ •၊၊||၊|။||||။‌‌‌‌‌၊|• ", "audio": arquivo, "id": hash(arquivo)})
                self.query_one(TextArea).mount(nova_mensagem)
        # elif event.button.id == "play":
        #     self.audio.play_audio()

    def on_key(self, event: Key):
        if event.key == "enter" and self.nome_user:
            input_widget = self.query_one(Input)
            if input_widget.value:
                if "//" in input_widget.value or "\\" in input_widget.value:
                    imagem_gerada = Controller.resize(input_widget.value)
                    if imagem_gerada:
                        pixel = Controller.gerar_pixel(imagem_gerada)
                        if pixel:
                            nome = Static(self.nome_user)
                            imagem_static = Static(pixel, name=hash(pixel))
                            self.query_one(TextArea).mount(nome, imagem_static)
                            self.mensagens.append(
                                {"autor": self.nome_user, "pixel": pixel, "id": hash(pixel)})
                            Banco.salvar("banco.db", "mensagens",
                                         self.mensagens)
                        else:
                            self.notify("ERRO com a imagem!")
                    else:
                        self.notify("ERRO com a imagem!")
                else:
                    nova_mensagem = Static(
                        f"{self.nome_user}\n  {input_widget.value}\n")
                    self.mensagens.append(
                        {"autor": self.nome_user, "mensagem": input_widget.value})
                    Banco.salvar("banco.db", "mensagens", self.mensagens)
                    self.query_one(TextArea).mount(nova_mensagem)
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
            encontrado = False
            for mensagem in self.mensagens:
                if "pixel" in mensagem.keys():
                    nome = Static(mensagem["autor"])
                    imagem_static = Static(
                        mensagem["pixel"], name=mensagem["id"])
                    for stt in self.query_one(TextArea).query(Static):
                        if stt.name == imagem_static.name:
                            encontrado = True
                            break
                    if not encontrado:
                        self.query_one(TextArea).mount(nome, imagem_static)
                elif "audio" in mensagem.keys():
                    stt = Static(
                        f"{mensagem["autor"]}\n  {mensagem["mensagem"]}\n", name=mensagem["id"])
                    self.audios[mensagem["id"]] = mensagem["audio"]
                    for stt_exibido in self.query_one(TextArea).query(Static):
                        if stt.name == imagem_static.name:
                            encontrado = True
                            break
                    if not encontrado:
                        self.query_one(TextArea).mount(stt)
                else:
                    stt = Static(
                        f"{mensagem["autor"]}\n  {mensagem["mensagem"]}\n")
                    for stt_exibido in self.query_one(TextArea).query(Static):
                        if stt.content == stt_exibido.content:
                            encontrado = True
                            break
                    if not encontrado:
                        self.query_one(TextArea).mount(stt)

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
            if carregar_msgs:
                self.mensagens = carregar_msgs
                encontrado = False
                for mensagem in self.mensagens:
                    if "pixel" in mensagem.keys():
                        nome = Static(mensagem["autor"])
                        imagem_static = Static(
                            mensagem["pixel"], name=mensagem["id"])
                        for stt in self.query_one(TextArea).query(Static):
                            if stt.name == imagem_static.name:
                                encontrado = True
                                break
                        if not encontrado:
                            self.query_one(TextArea).mount(nome, imagem_static)
                    elif "audio" in mensagem.keys():
                        stt = Static(
                            f"{mensagem["autor"]}\n  {mensagem["mensagem"]}\n", name=mensagem["id"])
                        self.audios[mensagem["id"]] = mensagem["audio"]
                        for stt_exibido in self.query_one(TextArea).query(Static):
                            if stt.name == imagem_static.name:
                                encontrado = True
                                break
                        if not encontrado:
                            self.query_one(TextArea).mount(stt)
                    else:
                        stt = Static(
                            f"{mensagem["autor"]}\n  {mensagem["mensagem"]}\n")
                        for stt_exibido in self.query_one(TextArea).query(Static):
                            if stt.content == stt_exibido.content:
                                encontrado = True
                                break
                        if not encontrado:
                            self.query_one(TextArea).mount(stt)

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
