import tempfile
from textual.screen import Screen
from textual.widgets import Input, TextArea, Static, ListItem, ListView, Header, Button, Footer
from textual.containers import HorizontalScroll, VerticalScroll, HorizontalGroup, Container
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
from PIL import Image
from rich_pixels import Pixels

from view.widgets import ChamadaVideo


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
    documentos = dict()
    atendeu = False
    chamada_em_curso = dict()

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
                        if blob[:3] == b'ID3' or (blob[0] == 0xFF and (blob[1] & 0xE0) == 0xE0):
                            blob = arquivo.export(buffer, format="mp3")
                        elif blob[:4] == b'OggS':
                            blob = arquivo.export(buffer, format="ogg")
                        elif blob[:4] == b'fLaC':
                            blob = arquivo.export(buffer, format="flac")
                        else:
                            return

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

                    if blob[:4] == b'RIFF':
                        sufixo = ".avi"
                    elif blob[4:8] == b'ftyp':
                        sufixo = ".mp4"
                    elif blob[:4] == b'\x1A\x45\xDF\xA3':
                        sufixo = ".mkv"
                    elif blob[:4] == b'OggS':
                        sufixo = ".ogv"
                    else:
                        return

                    with tempfile.NamedTemporaryFile(delete=False, suffix=sufixo) as tmp:
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
                    self.documentos[hash(
                        self.resultado["arquivo"])] = self.resultado["arquivo"]
                    self.mensagens.append(
                        {"autor": self.nome_user, "documento": self.resultado["arquivo"], "id": hash(self.resultado["arquivo"])})
                    Banco.salvar("banco.db", "mensagens",
                                 self.mensagens)

    async def on_click(self, evento: Click):
        if isinstance(evento.widget, Static):
            if "▶︎" in evento.widget.content:
                arquivo = self.audios[evento.widget.name]
                self.audio.tocar_audio(arquivo)
            if evento.widget.id == "selecionar_arquivo":
                await self.mount(TelaSelecionar.TelaSelecionar())
        if evento.widget.parent.parent.id == "lv_usuarios":
            if isinstance(evento.widget, Static):
                if "📞" in evento.widget.content:
                    Banco.salvar("banco.db", "chamada", {
                        self.nome_user: evento.widget.content[2:-2]})

    async def on_button_pressed(self, event: Button.Pressed) -> None:
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

        elif event.button.id == "bt_ligacao_true" or event.button.id == "bt_ligacao_false":
            await self.query_one("#container_call", Container).remove()
            Banco.deletar("banco.db", "chamada")
            Banco.salvar("banco.db", "chamata_atendida", False)
            if event.button.id == "bt_ligacao_true":
                self.atendeu = True
                Banco.salvar("banco.db", "chamata_atendida", True)
                self.ligacao()

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
                    blob = mensagem["video"]
                    if blob[:4] == b'RIFF':
                        sufixo = ".avi"
                    elif blob[4:8] == b'ftyp':
                        sufixo = ".mp4"
                    elif blob[:4] == b'\x1A\x45\xDF\xA3':
                        sufixo = ".mkv"
                    elif blob[:4] == b'OggS':
                        sufixo = ".ogv"
                    else:
                        return
                    with tempfile.NamedTemporaryFile(delete=False, suffix=sufixo) as tmp:
                        tmp.write(blob)
                        tmp_path = tmp.name
                    stt = Static((Video.Video(tmp_path)),
                                 name=mensagem["id"])
                    self.videos[mensagem["id"]] = blob
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

    montou_ligacao = False
    montou_caller = False
    salvou = False

    def ligacao(self):
        if not self.salvou:
            self.chamada_em_curso.append({self.nome_user: ""})
            Banco.salvar("banco.db", "chamada_em_curso", self.chamada_em_curso)
            self.salvou = True

        if self.montou_ligacao:
            container = self.get_child_by_id(
                "container_ligacao_em_curso")

            self.chamada_em_curso = Banco.carregar(
                "banco.db", "chamada_em_curso")

            if len(self.chamada_em_curso) > 1:

                for dict in self.chamada_em_curso:
                    for usuario, frame in dict.items():
                        if usuario != self.nome_user:
                            caller = usuario
                            frame = frame

                if not self.montou_caller:
                    receiver = ChamadaVideo.Receiver(id=caller)
                    receiver.update_frame(frame)
                    container.mount(receiver)
                else:
                    camera_caller = container.get_child_by_id(caller)
                    camera_caller.update_frame(frame)
            

        else:
            container = Container(id="container_ligacao_em_curso")
            self.mount(container)
            botao_desligar = Static("❌")
            botao_desligar.styles.height = 10
            botao_desligar.styles.width = 10
            container.mount(botao_desligar)
            stt_video = ChamadaVideo.Caller(id=self.nome_user)
            stt_video.nome_user = self.nome_user
            container.mount(stt_video)
            self.montou_ligacao = True

        # se a pessoa clicou para desligar a ligação aí faz self.montou_ligacao = False, self.atendeu = False

    montou_notificacao = False

    def poll_dados(self):
        if self.nome_user != "":

            chamada = Banco.carregar("banco.db", "chamada")
            if chamada:
                if self.nome_user in chamada.values() and not self.montou_notificacao:
                    container = Container(id="container_call")
                    self.mount(container)
                    container.mount(
                        Static(F"{chamada.keys()} está te ligando! Aceitar?"))
                    container.mount(Button("Sim", id="bt_ligacao_true"))
                    container.mount(Button("Não", id="bt_ligacao_false"))
                    self.montou_notificacao = True

            chamda_atendida = Banco.carregar("banco.db", "chamata_atendida")
            if chamda_atendida:
                self.ligacao()

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
                        blob = mensagem["video"]
                        if blob[:4] == b'RIFF':
                            sufixo = ".avi"
                        elif blob[4:8] == b'ftyp':
                            sufixo = ".mp4"
                        elif blob[:4] == b'\x1A\x45\xDF\xA3':
                            sufixo = ".mkv"
                        elif blob[:4] == b'OggS':
                            sufixo = ".ogv"
                        else:
                            return
                        with tempfile.NamedTemporaryFile(delete=False, suffix=sufixo) as tmp:
                            tmp.write(blob)
                            tmp_path = tmp.name
                        stt = Static((Video.Video(tmp_path)),
                                     name=mensagem["id"])
                        self.videos[mensagem["id"]] = blob
                        for stt_exibido in self.query_one(TextArea).query(Static):
                            if stt.name == stt.name:
                                encontrado = True
                                break
                        if not encontrado:
                            self.query_one(TextArea).mount(nome, stt)
                        pass

                    elif "documento":
                        self.documentos[mensagem["id"]] = mensagem["documento"]

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
                    ativos[f"🟢 {chave} 📞"] = valor
                else:
                    ativos[f"🔴 {chave}"] = valor
            return ativos

    def atualizar_usuario(self):
        agora = int(time.time())
        usuarios = Banco.carregar("banco.db", "usuarios")
        usuarios[self.nome_user] = agora
        Banco.salvar("banco.db", "usuarios", usuarios)
        self.users = self.listar_usuarios()

    def atualizar_lista_users(self, users):
        lista = self.query_one("#lv_usuarios", ListView)
        lista.remove_children()
        if users:
            for user in users.keys():
                lista.append(ListItem(Static(user)))
