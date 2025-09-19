import tempfile
from textual.screen import Screen
from textual.widgets import Input, TextArea, Static, ListItem, ListView, Header, Button, Footer
from textual.containers import HorizontalScroll, VerticalScroll, HorizontalGroup
from textual.events import Key
from textual.timer import Timer
from textual.events import Click
from database import Banco
import time
from model import Audio, Video, Imagem
import wave
from view import TelaSelecionar
from pydub import AudioSegment
import io


class TelaInicial(Screen):
    CSS_PATH = "css/TelaInicial.tcss"
    nome_user = ""
    users = dict()
    mensagens = list()
    _poll_timer: Timer = None
    audio = Audio.ChatVoz()
    audios = dict()
    obj_imagem = Imagem.Imagem()
    videos = dict()
    resultado = ""

    def compose(self):
        yield Header()
        with HorizontalScroll():
            with VerticalScroll():
                yield TextArea(read_only=True)
                with HorizontalGroup():
                    yield Input(placeholder="Digite aqui")
                    yield Static("📎", id="selecionar_arquivo")
                    yield Button("🔴", id="gravar")
            yield ListView(id="lv_usuarios")
        yield Footer()

    async def on_tela_selecionar_selecionado(self, message: TelaSelecionar.TelaSelecionar.Selecionado):
        self.resultado = message.valor

        if self.resultado:

            match self.resultado["tipo"]:

                case "imagem":
                    imagem_gerada = self.obj_imagem.resizeImagem(
                        self.resultado["arquivo"])
                    if imagem_gerada:
                        pixel = self.obj_imagem.gerar_pixel(
                            imagem_gerada)
                        if pixel:
                            nome = Static(self.nome_user)
                            imagem_static = Static(
                                pixel, name=hash(pixel))
                            self.query_one(TextArea).mount(
                                nome, imagem_static)
                            self.mensagens.append(
                                {"autor": self.nome_user, "pixel": pixel, "id": hash(pixel)})
                            Banco.salvar("banco.db", "mensagens",
                                         self.mensagens)

                case "audio":
                    nova_mensagem = Static(
                        f"{self.nome_user}\n  ▶︎ •၊၊||၊|။||||။‌‌‌‌‌၊|• \n", name=hash(self.resultado["arquivo"]))
                    self.audios[nova_mensagem.name] = self.resultado["arquivo"]
                    arquivo = self.resultado["arquivo"]
                    buffer = io.BytesIO()
                    if isinstance(arquivo, AudioSegment):
                        blob = arquivo.export(buffer, format="mp3")
                    elif isinstance(arquivo, wave.Wave_read):
                        with wave.open(buffer, "wb") as wf:
                            wf.setnchannels(arquivo.getnchannels())
                            wf.setsampwidth(arquivo.getsampwidth())
                            wf.setframerate(arquivo.getframerate())
                            wf.writeframes(arquivo.readframes(
                                arquivo.getnframes()))
                        blob = buffer.getvalue()
                    self.mensagens.append(
                        {"autor": self.nome_user, "mensagem": "▶︎ •၊၊||၊|။||||။‌‌‌‌‌၊|• ", "audio": blob, "id": hash(self.resultado["arquivo"])})
                    self.query_one(TextArea).mount(nova_mensagem)
                    Banco.salvar("banco.db", "mensagens",
                                 self.mensagens)

                case "video":

                    nome = Static(self.nome_user)
                    blob = self.resultado["arquivo"].read()

                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                        tmp.write(blob)
                        tmp_path = tmp.name

                    self.query_one(TextArea).mount(
                        nome, (Video.Video(tmp_path)))

                    self.videos[hash(self.resultado["arquivo"])] = blob
                    self.mensagens.append(
                        {"autor": self.nome_user, "video": blob, "id": hash(self.resultado["arquivo"])})
                    Banco.salvar("banco.db", "mensagens",
                                 self.mensagens)

                case "documento":
                    pass

    async def on_click(self, evento: Click):
        if isinstance(evento.widget, Static):
            if "▶︎" in evento.widget.content:
                arquivo = self.audios[evento.widget.name]
                self.audio.tocar_audio(arquivo)
            if evento.widget.id == "selecionar_arquivo":
                await self.mount(TelaSelecionar.TelaSelecionar())

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
                buffer = io.BytesIO()
                with wave.open(buffer, "wb") as wf:
                    wf.setnchannels(arquivo.getnchannels())
                    wf.setsampwidth(arquivo.getsampwidth())
                    wf.setframerate(arquivo.getframerate())
                    wf.writeframes(arquivo.readframes(
                        arquivo.getnframes()))
                blob = buffer.getvalue()
                nova_mensagem = Static(
                    f"{self.nome_user}\n  ▶︎ •၊၊||၊|။||||။‌‌‌‌‌၊|• \n", name=hash(arquivo))
                self.audios[nova_mensagem.name] = arquivo
                self.mensagens.append(
                    {"autor": self.nome_user, "mensagem": "▶︎ •၊၊||၊|။||||။‌‌‌‌‌၊|• ", "audio": blob, "id": hash(arquivo)})
                self.query_one(TextArea).mount(nova_mensagem)
                Banco.salvar("banco.db", "mensagens",
                             self.mensagens)
        # elif event.button.id == "play":
        #     self.audio.play_audio()

    def on_key(self, event: Key):
        if event.key == "enter" and self.nome_user:
            input_widget = self.query_one(Input)
            nova_mensagem = Static(
                f"{self.nome_user}\n  {str(input_widget.value)}\n")
            self.mensagens.append(
                {"autor": self.nome_user, "mensagem": str(input_widget.value)})
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

                    buffer = mensagem["audio"]
                    if not isinstance(buffer, bytes):
                        buffer.seek(0)
                        blob = buffer.read()
                    else:
                        blob = mensagem["audio"]

                    if blob[:4] == b'RIFF':
                        buffer = io.BytesIO(blob)
                        audio = wave.open(buffer, "rb")
                    elif blob[:3] == b'ID3' or (blob[0] == 0xFF and (blob[1] & 0xE0) == 0xE0):
                        audio = AudioSegment.from_file(
                            io.BytesIO(blob), format="mp3")
                    elif blob[:4] == b'OggS':
                        audio = AudioSegment.from_file(
                            io.BytesIO(blob), format="ogg")
                    elif blob[:4] == b'fLaC':
                        audio = AudioSegment.from_file(
                            io.BytesIO(blob), format="flac")
                    else:
                        return

                    self.audios[mensagem["id"]] = audio

                    for stt_exibido in self.query_one(TextArea).query(Static):
                        if stt_exibido.name == stt.name:
                            encontrado = True
                            break
                    if not encontrado:
                        self.query_one(TextArea).mount(stt)

                elif "video":
                    nome = Static(mensagem["autor"])
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                        tmp.write(mensagem["video"])
                        tmp_path = tmp.name
                    stt = Static((Video.Video(tmp_path)),
                                 name=mensagem["id"])
                    self.videos[mensagem["id"]] = mensagem["video"]
                    for stt_exibido in self.query_one(TextArea).query(Static):
                        if stt.name == stt.name:
                            encontrado = True
                            break
                    if not encontrado:
                        self.query_one(TextArea).mount(nome, stt)
                    pass

                elif "documentos":
                    pass

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

                        buffer = mensagem["audio"]
                        if not isinstance(buffer, bytes):
                            buffer.seek(0)
                            blob = buffer.read()
                        else:
                            blob = mensagem["audio"]

                        if blob[:4] == b'RIFF':
                            buffer = io.BytesIO(blob)
                            audio = wave.open(buffer, "rb")
                        elif blob[:3] == b'ID3' or (blob[0] == 0xFF and (blob[1] & 0xE0) == 0xE0):
                            audio = AudioSegment.from_file(
                                io.BytesIO(blob), format="mp3")
                        elif blob[:4] == b'OggS':
                            audio = AudioSegment.from_file(
                                io.BytesIO(blob), format="ogg")
                        elif blob[:4] == b'fLaC':
                            audio = AudioSegment.from_file(
                                io.BytesIO(blob), format="flac")
                        else:
                            return

                        self.audios[mensagem["id"]] = audio

                        for stt_exibido in self.query_one(TextArea).query(Static):
                            if stt_exibido.name == stt.name:
                                encontrado = True
                                break
                        if not encontrado:
                            self.query_one(TextArea).mount(stt)

                    elif "video":
                        nome = Static(mensagem["autor"])
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                            tmp.write(mensagem["video"])
                            tmp_path = tmp.name
                        stt = Static((Video.Video(tmp_path)),
                                     name=mensagem["id"])
                        self.videos[mensagem["id"]] = mensagem["video"]
                        for stt_exibido in self.query_one(TextArea).query(Static):
                            if stt.name == stt.name:
                                encontrado = True
                                break
                        if not encontrado:
                            self.query_one(TextArea).mount(nome, stt)
                        pass

                    elif "documentos":
                        pass

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
