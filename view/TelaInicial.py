import tempfile
import time
import wave
import io

from textual.screen import Screen
from textual.widgets import Input, Static, ListItem, ListView, Header, Footer, ProgressBar, Button
from textual.containers import HorizontalScroll, VerticalScroll, HorizontalGroup, Container
from textual.events import Key
from textual.timer import Timer
from textual.events import Click

from rich_pixels import Pixels

from database import Banco
from model import Audio, Imagem, Download, Usuario
from view.widgets import Video

from pydub import AudioSegment


class TelaInicial(Screen):
    CSS_PATH = "css/TelaInicial.tcss"
    users = dict()
    mensagens = list()
    _poll_timer: Timer = None
    audio = Audio.ChatVoz()
    audios = dict()
    obj_imagem = Imagem.Imagem()
    videos = dict()
    resultado = ""
    documentos = dict()
    montou_container_foto = False
    usuario = Usuario.Usuario()

    def compose(self):
        yield Header()
        with HorizontalScroll():
            with VerticalScroll():
                yield VerticalScroll(id="vs_mensagens")
                with HorizontalGroup():
                    yield Input(placeholder="Digite aqui")
            yield ListView(id="lv_usuarios")
        yield Footer()

    def exibir_midia(self, dados):
        if dados:

            nome_user_static = Static(self.usuario.get_nome())
            if self.usuario.get_cor():
                nome_user_static.styles.color = self.usuario.get_cor()

            match dados["tipo"]:

                case "imagem":
                    imagem_gerada = self.obj_imagem.resizeImagem(
                        dados["arquivo"])
                    if imagem_gerada:
                        pixel = self.obj_imagem.gerar_pixel(
                            imagem_gerada)
                        if pixel:
                            imagem_static = Static(
                                pixel, name=hash(pixel))
                            self.query_one("#vs_mensagens", VerticalScroll).mount(
                                nome_user_static, imagem_static)
                            self.mensagens.append(
                                {"autor": self.usuario.get_nome(), "pixel": pixel, "id": hash(pixel)})
                            Banco.salvar("banco.db", "mensagens",
                                         self.mensagens)

                case "audio":
                    self.audios[hash(dados["arquivo"])] = dados["arquivo"]
                    arquivo = dados["arquivo"]
                    buffer = io.BytesIO()
                    blob = arquivo

                    if isinstance(arquivo, AudioSegment):
                        if blob[:3] == b'ID3' or (blob[0] == 0xFF and (blob[1] & 0xE0) == 0xE0):
                            blob = arquivo.export(buffer, format="mp3")
                        elif blob[:4] == b'OggS':
                            blob = arquivo.export(buffer, format="ogg")
                        elif blob[:4] == b'fLaC':
                            blob = arquivo.export(buffer, format="flac")
                        else:
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
                        {"autor": self.usuario.get_nome(), "audio": blob, "id": hash(dados["arquivo"])})
                    self.query_one("#vs_mensagens", VerticalScroll).mount(
                        nome_user_static, ProgressBar(name=hash(dados["arquivo"])))
                    Banco.salvar("banco.db", "mensagens",
                                 self.mensagens)

                case "video":

                    blob = dados["arquivo"].read()

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

                    self.query_one("#vs_mensagens", VerticalScroll).mount(
                        nome_user_static, Video.Video(tmp_path))

                    self.videos[hash(dados["arquivo"])] = blob
                    self.mensagens.append(
                        {"autor": self.usuario.get_nome(), "video": blob, "id": hash(dados["arquivo"])})
                    Banco.salvar("banco.db", "mensagens",
                                 self.mensagens)

                case "documento":
                    self.query_one("#vs_mensagens", VerticalScroll).mount(nome_user_static, Static(
                        dados["nome"], name=hash(dados["arquivo"])))
                    self.documentos[hash(
                        dados["arquivo"])] = dados["arquivo"]
                    self.mensagens.append(
                        {"autor": self.usuario.get_nome(), "documento": dados["arquivo"], "id": hash(dados["arquivo"])})
                    Banco.salvar("banco.db", "mensagens",
                                 self.mensagens)

    # def make_progress(self) -> None:
    #     self.query_one(ProgressBar).advance(1)

    def on_key(self, event: Key):
        if event.key == "enter" and self.usuario.get_nome():
            input_widget = self.query_one(Input)

            if self.montou_container_foto:
                try:
                    dados = Download.baixar_para_memoria_ou_temp(
                        input_widget.value)
                    imagem_gerada = self.obj_imagem.resize_imagem_com_tamanho(
                        dados["arquivo"], 5)
                    if imagem_gerada:
                        pixel = self.obj_imagem.gerar_pixel(
                            imagem_gerada)
                        if pixel:
                            imagem_static = Static(
                                pixel)
                            container = self.get_child_by_id("container_foto")
                            container.mount(imagem_static, before=0)
                            self.usuario.set_pixel_perfil(pixel)
                            self.users[self.usuario.get_nome()] = self.usuario
                            Banco.salvar("banco.db", "usuarios", self.users)
                except:
                    self.notify("ERRO!")

            elif "http" in input_widget.value or "https" in input_widget.value:
                try:
                    dados = Download.baixar_para_memoria_ou_temp(
                        input_widget.value)
                    self.exibir_midia(dados)
                except:
                    self.notify("Erro com Midia")

            else:
                self.notify(self.usuario.get_cor())
                nome_user_static = Static(self.usuario.get_nome())
                if self.usuario.get_cor():
                    nome_user_static.styles.color = self.usuario.get_cor()
                nova_mensagem = Static(str(input_widget.value))
                self.mensagens.append(
                    {"autor": self.usuario.get_nome(), "mensagem": str(input_widget.value)})
                Banco.salvar("banco.db", "mensagens", self.mensagens)
                self.query_one("#vs_mensagens", VerticalScroll).mount(
                    nome_user_static, nova_mensagem)
                input_widget.clear()

    async def on_click(self, evento: Click):

        if str(evento.widget) == "HeaderTitle()":
            if self.montou_container_foto:
                container = self.get_child_by_id("container_foto")
                container.remove()
                self.montou_container_foto = False

        if isinstance(evento.widget, ProgressBar):
            arquivo = self.audios[evento.widget.name]
            self.audio.tocar_audio(arquivo)

        if isinstance(evento.widget, Static):
            if "👤" in evento.widget.content:
                ctt_foto = Container(id="container_foto")
                ctt_foto.styles.layer = "above"
                ctt_foto.styles.width = "44%"
                ctt_foto.styles.height = "40%"
                ctt_foto.styles.align = ("center", "middle")
                self.mount(ctt_foto)
                ctt_foto.mount(Header(show_clock=False))
                # ctt_foto.get_child_by_type(Header).
                ctt_foto.mount(
                    Input(placeholder="caminho da foto"))
                self.montou_container_foto = True
            # else:
            #     documento = self.documentos[evento.widget.name]
            # TODO: abrir documento, ou abrir foto dele montou_container_foto

    def on_mount(self):
        users = self.listar_usuarios()
        self.atualizar_lista_users(users)
        self.poll_dados()

        self._poll_timer = self.set_interval(2, self.poll_dados)

    def poll_dados(self):
        if self.usuario.get_nome() != "":

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

                    stt_nome_autor = Static(mensagem["autor"])
                    if self.users[mensagem["autor"]].get_cor():
                        stt_nome_autor.styles.color = self.users[mensagem["autor"]].get_cor(
                        )

                    if "pixel" in mensagem.keys():

                        imagem_static = Static(
                            mensagem["pixel"], name=mensagem["id"])
                        for stt in self.query_one("#vs_mensagens", VerticalScroll).query(Static):
                            if stt.name == imagem_static.name:
                                encontrado = True
                                break
                        if not encontrado:
                            self.query_one("#vs_mensagens", VerticalScroll).mount(
                                stt_nome_autor, imagem_static)

                    elif "audio" in mensagem.keys():
                        bar = ProgressBar(name=mensagem["id"])

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

                        for progressbar_exibidas in self.query_one("#vs_mensagens", VerticalScroll).query(ProgressBar):
                            if progressbar_exibidas.name == bar.name:
                                encontrado = True
                                break
                        if not encontrado:
                            self.query_one("#vs_mensagens", VerticalScroll).mount(
                                stt_nome_autor, bar)

                    elif "video" in mensagem.keys():
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
                        for stt_exibido in self.query_one("#vs_mensagens", VerticalScroll).query(Static):
                            if stt.name == stt.name:
                                encontrado = True
                                break
                        if not encontrado:
                            self.query_one("#vs_mensagens", VerticalScroll).mount(
                                stt_nome_autor, stt)
                        pass

                    elif "documento" in mensagem.keys():
                        self.documentos[mensagem["id"]] = mensagem["documento"]

                    else:
                        mensagem = Static(mensagem["mensagem"])
                        lista = list(self.query_one(
                            "#vs_mensagens", VerticalScroll).query(Static))
                        encontrado = False

                        for stt_exibido in lista:
                            if stt_exibido.content.strip() == stt_nome_autor.content.strip():
                                index = lista.index(stt_exibido)
                                if index + 1 < len(lista):
                                    depois = lista[index + 1]
                                    if depois.content.strip() == mensagem.content.strip():
                                        encontrado = True
                                        break

                        if not encontrado:
                            self.query_one("#vs_mensagens", VerticalScroll).mount(
                                stt_nome_autor, mensagem)

    def listar_usuarios(self):
        if self.usuario.get_nome() != "":
            agora = int(time.time())
            usuarios = Banco.carregar("banco.db", "usuarios") or {}
            ativos = {}
            for chave, valor in usuarios.items():
                if agora - valor.get_tempo() <= 60:
                    ativos[f"👤 🟢 {chave}"] = valor
                else:
                    ativos[f"👤 🔴 {chave}"] = valor
            return ativos

    def atualizar_usuario(self):
        agora = int(time.time())
        usuarios = Banco.carregar("banco.db", "usuarios") or {}
        usuarios[self.usuario.get_nome()].set_tempo(agora)
        Banco.salvar("banco.db", "usuarios", usuarios)
        self.users = self.listar_usuarios()

    def atualizar_lista_users(self, users):
        lista = self.query_one("#lv_usuarios", ListView)
        lista.remove_children()
        if users:
            for chave, user in users.items():
                nome_user = Static(chave)
                if user.get_cor():
                    nome_user.styles.color = user.get_cor()

                if user.get_pixel_perfil():
                    lst_item = ListItem()
                    lst_item.styles.layout = "horizontal"
                    lista.append(lst_item)
                    lst_item.mount(Static(user.get_pixel_perfil()), nome_user)
                else:
                    lista.append(ListItem(nome_user))
