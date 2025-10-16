import asyncio
import time
import io
import json
import base64

from textual.screen import Screen
from textual.widgets import TextArea, Button, Static, ListItem, ListView, Header, Footer
from textual.containers import HorizontalScroll, Grid, Horizontal, VerticalScroll, HorizontalGroup, Container, Vertical
from textual.events import Click

from textual_image.widget import SixelImage
from textual_image.widget import HalfcellImage

from textual_filedrop import FileDrop
from textual_pdf.pdf_viewer import PDFViewer

import websockets

from database.Banco import Banco
from model import Usuario
from view.widgets import Audio, Video


import ssl


class ContainerDocumento(Container):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_mount(self):
        self.styles.layer = "above"

    def compose(self):
        yield Button("❌")

    async def on_button_pressed(self):
        await self.remove()


class ContainerLigacao(Container):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_mount(self):
        self.styles.layer = "above"

    def compose(self):
        with Horizontal():
            yield Button("❌")
            yield Static("ᑕᕼᗩᗰᗩᗪᗩ", id="titulo")
        with Grid(id="cameras"):
            pass

    def on_button_pressed(self):
        Banco.salvar_um("Acao", "stop_video")


class ContainerMessageLigacao(Container):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_mount(self):
        self.styles.layer = "above"

    def compose(self):
        yield Static(F"está te ligando! Aceitar?")
        with HorizontalGroup():
            yield Button("Sim", id="bt_ligacao_true")
            yield Button("Não", id="bt_ligacao_false")

    async def on_button_pressed(self, evento: Button.Pressed):
        await self.remove()
        Banco.deletar("banco.db", "chamada")  # TODO: Arrumar
        if evento.button.id == "bt_ligacao_true":
            Banco.salvar_um("Acao", "video")
        # else:
        #     self.screen.montou_ligacao = False
        #     self.screen.atendeu = False
        #     self.screen.montou_caller = False
        #     self.screen.montou_notificacao = False


class TelaInicial(Screen):
    CSS_PATH = "css/TelaInicial.tcss"

    usuario = Usuario.Usuario()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mensagens = list()
        self._poll_timer = None
        self.frame_task = None
        self.filedrop_perfil = False
        self.url = Banco.carregar_um("Url")
        self.is_recording = False
        self.montou_notificacao = False
        self.iniciou_frames = False
        self.parou_frames = False
        self.frames_audio = []
        self.documentos = dict()

    async def receber_frames(self):
        print("receber_frames", self.usuario.get_nome())
        nova_url = (
            self.url.replace(
                "https://", "wss://").replace("http://", "ws://").rstrip("/") + "/ws"
        )
        print(nova_url)
        while True:  # TODO: Ficar conectando cria vários processos python e mata a RAM do pc
            try:
                print("antes de async with websockets.connect(nova_url)",
                      self.usuario.get_nome())

                if "https" in self.url:
                    ssl_context = ssl._create_unverified_context()
                    async with websockets.connect(nova_url, ssl=ssl_context) as ws:

                        print(
                            "depois de async with websockets.connect(nova_url)", self.usuario.get_nome())
                        self.ws_ativo = True

                        blob = await ws.recv()
                        acao = Banco.carregar_um("Acao")

                        try:
                            if isinstance(blob, bytes):
                                blob = blob.decode("utf-8")
                            data = json.loads(blob)
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            continue

                        frame_bytes = base64.b64decode(data["data"])
                        novo_frame = io.BytesIO(frame_bytes)

                        if acao == "video":
                            Banco.salvar_seguro_chamada({self.usuario.get_nome(): novo_frame}
                                                        )
                        else:
                            self.frames_audio.append(novo_frame)

                        novo_frame.close()
                        del novo_frame
                        print("depois de Banco2.Banco.salvar_seguro",
                              self.usuario.get_nome())

                else:
                    async with websockets.connect(nova_url) as ws:

                        print(
                            "depois de async with websockets.connect(nova_url)", self.usuario.get_nome())
                        self.ws_ativo = True

                        blob = await ws.recv()
                        acao = Banco.carregar_um("Acao")
                        if acao != "video":
                            continue
                        try:
                            if isinstance(blob, bytes):
                                blob = blob.decode("utf-8")
                            data = json.loads(blob)
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            continue

                        frame_bytes = base64.b64decode(data["data"])
                        novo_frame = io.BytesIO(frame_bytes)

                        if acao == "video":
                            Banco.salvar_seguro_chamada({self.usuario.get_nome(): novo_frame}
                                                        )
                        else:
                            self.frames_audio.append(novo_frame)

                        novo_frame.close()
                        del novo_frame
                        print("depois de Banco2.Banco.salvar_seguro",
                              self.usuario.get_nome())

            except Exception as e:
                print(f"Erro na conexão WebSocket: {e}")
                self.ws_ativo = False
                await asyncio.sleep(5)

    def start_receber_frames(self):
        print("start_receber_frames")
        loop = asyncio.get_event_loop()
        self.frame_task = loop.create_task(self.receber_frames())

    def stop_receber_frames(self):
        if self.frame_task:
            self.frame_task.cancel()

    async def on_mount(self):
        print("on_mount", self.usuario.get_nome())

        self.query_one("#lv_grupos", ListView).append(Static("Grupos:"))
        self.query_one("#lv_grupos", ListView).append(
            Static("Adicionar Grupo:"))
        self.query_one("#lv_grupos", ListView).append(
            ListItem(Static(" >Senac")))
        self.query_one("#lv_grupos", ListView).append(
            ListItem(Static("    👤 🟢 Lucas")))

        users = self.listar_usuarios()
        self.atualizar_lista_users(users)
        self.poll_dados()

        self._poll_timer = self.set_interval(2, self.poll_dados)

    def compose(self):
        yield Header()
        with HorizontalScroll():
            yield ListView(id="lv_grupos")
            with VerticalScroll():
                yield VerticalScroll(id="vs_mensagens")
                with HorizontalGroup():
                    yield TextArea(placeholder="Digite aqui")
                    yield Button("Enviar", id="bt_enviar_mensagem")
                    yield Button("📎", id="bt_filedrop")
                    yield Button("🔴", id="gravar")
            yield ListView(id="lv_usuarios")
        yield Footer()

    def action_pdf(self, hash):
        container = ContainerDocumento()
        self.mount(container)
        blob = self.documentos[hash]
        container.mount(PDFViewer(blob))

    def on_file_drop_dropped(self, event: FileDrop.Dropped) -> None:
        try:
            nome = "".join(event.filenames[-1])
            ext = nome[nome.index("."):]
            caminho = "".join(event.filepaths)

            tipo = ""
            if ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
                tipo = "imagem"
            elif ext in [".mp4", ".mov", ".avi", ".mkv", ".webm"]:
                tipo = "video"
            elif ext in [".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac"]:
                tipo = "audio"
            else:
                tipo = "documento"

            with open(caminho, "rb") as f:
                blob = f.read()

            if self.filedrop_perfil:
                if tipo == "imagem":
                    self.usuario.set_pixel_perfil(blob)
                    Banco.atualizar("Usuario", "foto",
                                    self.usuario.get_cor(), blob)
                else:
                    self.notify("ERRO: Arquivo não é imagem!")
                self.filedrop_perfil = False

            dados = {"autor": self.usuario.get_nome(), "arquivo": blob,
                     "tipo": tipo, "nome": nome, "hash": hash(blob)}
            Banco.salvar_mensagem(dados)

        except Exception as e:
            self.notify(str(e))

        self.query_one(FileDrop).remove()

    async def on_button_pressed(self, event: Button.Pressed):
        input_widget = self.query_one(TextArea)
        nome_user_static = Static(
            self.usuario.get_nome(), classes="stt_usuario")

        match event.button.id:
            case "bt_filedrop":
                try:
                    self.query_one(FileDrop).remove()
                except:
                    self.mount(FileDrop())

            case "gravar":
                if not self.is_recording:
                    Banco.salvar_um("Acao", "audio")
                    self.start_receber_frames()
                    self.query_one("#gravar", Button).label = "⬛"
                    self.query_one(TextArea).disabled = True
                    self.query_one(TextArea).text = "▶• Gravando..."
                else:
                    Banco.salvar_um("Acao", "stop_audio")
                    self.stop_receber_frames()
                    self.query_one("#gravar", Button).label = "🔴"
                    self.query_one(TextArea).disabled = False
                    self.query_one(TextArea).text = ""

                    audio_final = io.BytesIO(
                        b"".join(f.getvalue() for f in self.frames_audio))

                    Banco.salvar_mensagem(
                        {"autor": self.usuario.get_nome(), "audio": audio_final.getvalue(), "id": hash(self.frames_audioivo), "nome": ""})

                    self.query_one("#vs_mensagens", VerticalScroll).mount(
                        nome_user_static, Audio.Audio(audio_final.getvalue(), name=hash(self.frames_audio)))

                    self.frames_audio = []

            case _:

                if input_widget.text:
                    if self.usuario.get_cor():
                        nome_user_static.styles.color = self.usuario.get_cor()

                    nova_mensagem = Static(str(input_widget.text))
                    Banco.salvar_mensagem(
                        {"autor": self.usuario.get_nome(), "mensagem": str(input_widget.text)})

                    self.query_one("#vs_mensagens", VerticalScroll).mount(
                        nome_user_static, nova_mensagem)

    def on_click(self, evento: Click):
        if evento.widget.parent.parent.id == "lv_usuarios":
            if isinstance(evento.widget, Static):
                if "📞" in evento.widget.content:
                    # Banco.salvar("banco.db", "chamada", {
                    #     self.usuario.get_nome(): evento.widget.content[4:-2]})
                    pass  # TODO: arrumar
                elif "👤" in evento.widget.content:
                    try:
                        self.query_one(FileDrop).remove()
                        self.filedrop_perfil = False
                    except:
                        self.mount(FileDrop())
                        self.query_one(FileDrop).focus()
                        self.filedrop_perfil = True

    def ligacao(self):
        try:
            try:
                container = self.query_one(ContainerLigacao)
            except:
                container = ContainerLigacao()
                self.mount(container)

            chamada_em_curso = Banco.carregar_frames() or {}

            if chamada_em_curso:
                for usuario, frame in chamada_em_curso.items():
                    try:
                        camera = None
                        for vertical in container.query_one("#cameras").query(Vertical):
                            camera_procurando = ""
                            if self.app.servidor == True:
                                camera_procurando = vertical.query_one(
                                    HalfcellImage)
                            else:
                                camera_procurando = vertical.query_one(
                                    SixelImage)

                            if camera_procurando and camera_procurando.name == usuario:
                                camera = camera_procurando
                                break

                        if not camera:
                            raise Exception
                        else:
                            camera.image = frame

                    except Exception as e:
                        vt = Vertical()
                        container.query_one("#cameras").mount(vt)
                        if self.app.servidor == True:
                            camera = HalfcellImage(pixel=True, name=usuario)
                        else:
                            camera = SixelImage(frame, name=usuario)

                        camera.image = frame
                        vt.mount(camera)
                        vt.mount(Static(usuario.capitalize()))

        except Exception as e:
            print(f"Erro em ligacao(): {e}")

    def poll_dados(self):
        acao = Banco.carregar_um("Acao")
        if acao == "video" and self.iniciou_frames == False:
            self.start_receber_frames()
            self.iniciou_frames = True
        elif acao == "stop-video" and self.parou_frames == False:
            self.iniciou_frames = False
            self.parou_frames = True
            self.stop_receber_frames()
            self.atendeu = False
            self.montou_notificacao = False
            self.query_one(ContainerLigacao).remove()

        chamada_curso = Banco.carregar_frames() or {}

        if chamada_curso:
            self.ligacao()

        chamada = Banco.carregar("banco.db", "chamada")  # TODO: arrumar
        if chamada:
            if self.usuario.get_nome() in chamada.values() and self.montou_notificacao == False:
                container = ContainerMessageLigacao()
                self.mount(container)
                container.query_one(Static).update(
                    F"{next(iter(chamada.keys()))} está te ligando! Aceitar?")
                self.montou_notificacao = True

        self.atualizar_usuario()

        self.exibir_midia()

    def exibir_midia(self):
        users = self.listar_usuarios()

        dados = Banco.carregar_mensagens()

        carregar_users = Banco.carregar_usuarios()
        if carregar_users:
            self.atualizar_lista_users(users)

        if dados:
            self.mensagens = dados

            for dados in self.mensagens:
                encontrado = False

                stt_nome_autor = Static(
                    dados["autor"], classes="stt_usuario")

                if carregar_users[dados["autor"]].get_cor():
                    stt_nome_autor.styles.color = carregar_users[dados["autor"]].get_cor(
                    )

                match dados["tipo"]:

                    case "imagem":
                        for stt in self.query_one("#vs_mensagens", VerticalScroll).query(HalfcellImage):
                            if stt.name == dados["hash"]:
                                encontrado = True
                                break

                            if encontrado == False:
                                for stt in self.query_one("#vs_mensagens", VerticalScroll).query(SixelImage):
                                    if stt.name == dados["hash"]:
                                        encontrado = True
                                        break

                        if encontrado == False:
                            if self.app.servidor == True:
                                imagem_static = HalfcellImage(io.BytesIO(
                                    dados["arquivo"]), name=dados["hash"])
                            else:
                                imagem_static = SixelImage(io.BytesIO(
                                    dados["arquivo"]), name=dados["hash"])
                            imagem_static.styles.width = 35
                            imagem_static.styles.height = 13
                            imagem_static.styles.margin = (0, 0, 0, 4)
                            imagem_static.styles.background = "0%"

                        self.query_one("#vs_mensagens", VerticalScroll).mount(
                            stt_nome_autor, imagem_static)

                    case "audio":
                        for audio_exibidos in self.query_one("#vs_mensagens", VerticalScroll).query(Audio.Audio):
                            if audio_exibidos.name == dados["hash"]:
                                encontrado = True
                                break

                        if encontrado == False:
                            bar = Audio.Audio(
                                dados["arquivo"], mensagem["nome"], name=dados["hash"])
                            self.query_one("#vs_mensagens", VerticalScroll).mount(
                                stt_nome_autor, bar)

                    case "video":
                        for videos_exibidos in self.query_one("#vs_mensagens", VerticalScroll).query(Video.Video):
                            if videos_exibidos.name == dados["hash"]:
                                encontrado = True
                                break
                        if encontrado == False:
                            if self.app.servidor == True:
                                stt = Video.Video(
                                    dados["arquivo"], name=dados["hash"], pixel=True)
                            else:
                                stt = Video.Video(
                                    dados["arquivo"], name=dados["hash"])

                            self.query_one("#vs_mensagens", VerticalScroll).mount(
                                stt_nome_autor, stt)

                    case "documento":
                        lista = list(self.query_one(
                            "#vs_mensagens", VerticalScroll).query(Static))
                        for stt_exibido in lista:
                            content = stt_exibido.content
                            if content.strip() == stt_nome_autor.content.strip():
                                index = lista.index(stt_exibido)
                                if index + 1 < len(lista):
                                    depois = lista[index + 1]
                                    if hasattr(depois.content, 'strip') and isinstance(depois.content, str):
                                        if depois.name == dados["hash"]:
                                            encontrado = True
                                            break
                                    else:
                                        break

                        if encontrado == False:
                            nome = dados["hash"]
                            self.documentos[dados["hash"]] = dados["blob"]

                            self.query_one("#vs_mensagens", VerticalScroll).mount(stt_nome_autor, Static(
                                f"[@click=self.pdf('{hash}')]{nome}[/]",
                                name=dados["hash"])  # TODO: Arrumar
                            )

                    case _:
                        mensagem = Static(mensagem["mensagem"])
                        lista = list(self.query_one(
                            "#vs_mensagens", VerticalScroll).query(Static))
                        for stt_exibido in lista:
                            content = stt_exibido.content
                            if content.strip() == stt_nome_autor.content.strip():
                                index = lista.index(stt_exibido)
                                if index + 1 < len(lista):
                                    depois = lista[index + 1]
                                    if hasattr(depois.content, 'strip') and isinstance(depois.content, str):
                                        if depois.name == dados["hash"]:
                                            encontrado = True
                                            break
                                    else:
                                        break

                        if not encontrado:
                            self.query_one("#vs_mensagens", VerticalScroll).mount(
                                stt_nome_autor, mensagem)

    def listar_usuarios(self):
        if self.usuario.get_nome() != "":
            agora = int(time.time())
            usuarios = Banco.carregar_usuarios() or {}
            ativos = {}
            for chave, valor in usuarios.items():
                if valor:
                    if agora - valor.get_tempo() <= 60:
                        ativos[f"👤 🟢 {chave} 📞"] = valor
                    else:
                        ativos[f"👤 🔴 {chave}"] = valor
            return ativos

    def atualizar_usuario(self):
        agora = int(time.time())
        Banco.atualizar("Usuario", "tempo", self.usuario.get_cor(), agora)

    def atualizar_lista_users(self, users):
        lista = self.query_one("#lv_usuarios", ListView)
        lista.remove_children()
        lista.append(Static("Usuários:"))

        if users:
            for chave, user in users.items():
                nome_user = Static(chave)
                if user.get_cor():
                    nome_user.styles.color = user.get_cor()

                if user.get_pixel_perfil():
                    lst_item = ListItem()
                    lst_item.styles.layout = "horizontal"
                    lista.append(lst_item)
                    if self.app.servidor == True:
                        imagem_static = HalfcellImage(io.BytesIO(
                            user.get_pixel_perfil()), id="stt_foto_perfil")
                    else:
                        imagem_static = SixelImage(io.BytesIO(
                            user.get_pixel_perfil()), id="stt_foto_perfil")

                    imagem_static.styles.width = 5
                    imagem_static.styles.height = 5
                    imagem_static.styles.background = "0%"
                    lst_item.mount(imagem_static, nome_user)
                else:
                    lista.append(ListItem(nome_user))
