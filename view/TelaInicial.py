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

    async def on_button_pressed(self):
        if self.screen.ws:
            await self.screen.ws.send(json.dumps(["action", "stop_video"]))


class ContainerMessageLigacao(Container):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_mount(self):
        self.styles.layer = "above"

    def compose(self):
        yield Static("está te ligando! Aceitar?")
        with HorizontalGroup():
            yield Button("Sim", id="bt_ligacao_true")
            yield Button("Não", id="bt_ligacao_false")

    async def on_button_pressed(self, evento: Button.Pressed):
        await self.remove()
        if evento.button.id == "bt_ligacao_true":
            if self.screen.ws:
                await self.screen.ws.send(json.dumps(["action", "video"]))


class TelaInicial(Screen):
    CSS_PATH = "css/TelaInicial.tcss"

    usuario = Usuario.Usuario()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.frame_task = None
        self.filedrop_perfil = False
        self.banco = Banco()
        self.url = self.banco.carregar_um("Url")
        self.is_recording = False
        self.montou_notificacao = False
        self.iniciou_frames = False
        self.parou_frames = False
        self.frames_audio = []
        self.documentos = dict()
        self.ws = None
        self.acao = ""

    async def receber_frames(self):
        nova_url = (
            self.url.replace(
                "https://", "wss://").replace("http://", "ws://").rstrip("/") + "/ws"
        )
        while True:
            try:
                if "https" in self.url:
                    ssl_context = ssl._create_unverified_context()
                    async with websockets.connect(nova_url, ssl=ssl_context) as ws:
                        self.ws = ws
                        await self.send_user_update()
                        while True:
                            msg = await ws.recv()
                            if isinstance(msg, bytes):
                                if self.is_recording:
                                    self.frames_audio.append(io.BytesIO(msg))
                                elif self.acao == "video":
                                    self.handle_video_frame(
                                        "unknown", io.BytesIO(msg))
                            else:
                                envelope = json.loads(msg)
                                type_ = envelope[0]
                                data = envelope[1]
                                if type_ == "message":
                                    await self.handle_message(data)
                                elif type_ == "action":
                                    self.acao = data
                                    if data == "video" and not self.iniciou_frames:
                                        self.iniciou_frames = True
                                    elif data == "stop_video" and not self.parou_frames:
                                        self.iniciou_frames = False
                                        self.parou_frames = True
                                        try:
                                            self.query_one(
                                                ContainerLigacao).remove()
                                        except:
                                            pass
                                    elif data == "audio":
                                        self.is_recording = True
                                    elif data == "stop_audio":
                                        self.is_recording = False
                                        audio_final = io.BytesIO(
                                            b"".join(f.getvalue() for f in self.frames_audio))
                                        hash_val = hash(audio_final.getvalue())
                                        dados = {
                                            "autor": self.usuario.get_nome(),
                                            "tipo": "audio",
                                            "arquivo": base64.b64encode(audio_final.getvalue()).decode(),
                                            "nome": "",
                                            "hash": hash_val
                                        }
                                        await ws.send(json.dumps(["message", dados]))
                                        self.frames_audio = []
                                elif type_ == "user_update":
                                    self.handle_user_update(data)
                                elif type_ == "call":
                                    if data["receiver"] == self.usuario.get_nome() and not self.montou_notificacao:
                                        container = ContainerMessageLigacao()
                                        self.mount(container)
                                        container.query_one(Static).update(
                                            f"{data['caller']} está te ligando! Aceitar?")
                                        self.montou_notificacao = True
                else:
                    async with websockets.connect(nova_url) as ws:
                        self.ws = ws
                        await self.send_user_update()
                        while True:
                            msg = await ws.recv()
                            if isinstance(msg, bytes):
                                if self.is_recording:
                                    self.frames_audio.append(io.BytesIO(msg))
                                elif self.acao == "video":
                                    self.handle_video_frame(
                                        "unknown", io.BytesIO(msg))
                            else:
                                envelope = json.loads(msg)
                                type_ = envelope[0]
                                data = envelope[1]
                                if type_ == "message":
                                    await self.handle_message(data)
                                elif type_ == "action":
                                    self.acao = data
                                    if data == "video" and not self.iniciou_frames:
                                        self.iniciou_frames = True
                                    elif data == "stop_video" and not self.parou_frames:
                                        self.iniciou_frames = False
                                        self.parou_frames = True
                                        try:
                                            self.query_one(
                                                ContainerLigacao).remove()
                                        except:
                                            pass
                                    elif data == "audio":
                                        self.is_recording = True
                                    elif data == "stop_audio":
                                        self.is_recording = False
                                        audio_final = io.BytesIO(
                                            b"".join(f.getvalue() for f in self.frames_audio))
                                        hash_val = hash(audio_final.getvalue())
                                        dados = {
                                            "autor": self.usuario.get_nome(),
                                            "tipo": "audio",
                                            "arquivo": base64.b64encode(audio_final.getvalue()).decode(),
                                            "nome": "",
                                            "hash": hash_val
                                        }
                                        await ws.send(json.dumps(["message", dados]))
                                        self.frames_audio = []
                                elif type_ == "user_update":
                                    self.handle_user_update(data)
                                elif type_ == "call":
                                    if data["receiver"] == self.usuario.get_nome() and not self.montou_notificacao:
                                        container = ContainerMessageLigacao()
                                        self.mount(container)
                                        container.query_one(Static).update(
                                            f"{data['caller']} está te ligando! Aceitar?")
                                        self.montou_notificacao = True
            except Exception as e:
                print("Erro na conexão WebSocket:", e)
                self.ws = None
                await asyncio.sleep(5)

    async def on_mount(self):
        print("on_mount", self.usuario.get_nome())
        self.query_one("#lv_grupos", ListView).append(Static("Grupos:"))
        self.query_one("#lv_grupos", ListView).append(
            Static("Adicionar Grupo:"))
        self.query_one("#lv_grupos", ListView).append(
            ListItem(Static(" >Senac")))
        self.query_one("#lv_grupos", ListView).append(
            ListItem(Static("    👤 🟢 Lucas")))
        mensagens = self.banco.carregar_mensagens() or []
        for dados in mensagens:
            await self.handle_message(dados)
        self.atualizar_lista_users(self.listar_usuarios())
        self.frame_task = asyncio.create_task(self.receber_frames())
        self.set_interval(30, self.send_user_update)

    def compose(self):
        yield Header()
        with HorizontalScroll():
            yield ListView(id="lv_grupos")
            with VerticalScroll():
                yield VerticalScroll(id="vs_mensagens")
                with HorizontalGroup(id="footer_send"):
                    yield TextArea(placeholder="Digite aqui")
                    yield Button("Enviar", id="bt_enviar_mensagem")
                    yield Button("📎", id="bt_filedrop")
                    yield Button("🔴", id="gravar")
            yield ListView(id="lv_usuarios")
        yield Footer()

    async def send_user_update(self):
        agora = int(time.time())
        user_data = {
            "nome": self.usuario.get_nome(),
            "cor": self.usuario.get_cor(),
            "foto": base64.b64encode(self.usuario.get_foto()).decode() if self.usuario.get_foto() else "",
            "tempo": agora
        }
        self.banco.atualizar("Usuario", "tempo", "cor",
                             agora, self.usuario.get_cor())
        if self.ws:
            await self.ws.send(json.dumps(["user_update", user_data]))

    async def handle_message(self, data):
        encontrado = False
        stt_nome_autor = Static(data["autor"], classes="stt_usuario")
        for user in self.banco.carregar_usuarios():
            if user.get_nome() == data["autor"] and user.get_cor():
                stt_nome_autor.styles.color = user.get_cor()
                break
        tipo = data["tipo"]
        arquivo = data["arquivo"]
        if tipo in ["imagem", "audio", "video", "documento"]:
            arquivo = base64.b64decode(arquivo)
        match tipo:
            case "imagem":
                for stt in self.query_one("#vs_mensagens", VerticalScroll).query(HalfcellImage):
                    if stt.name == data["hash"]:
                        encontrado = True
                        break
                if not encontrado:
                    for stt in self.query_one("#vs_mensagens", VerticalScroll).query(SixelImage):
                        if stt.name == data["hash"]:
                            encontrado = True
                            break
                if not encontrado:
                    imagem_static = HalfcellImage(io.BytesIO(arquivo), name=data["hash"]) if self.app.servidor else SixelImage(
                        io.BytesIO(arquivo), name=data["hash"])
                    imagem_static.styles.width = 35
                    imagem_static.styles.height = 13
                    imagem_static.styles.margin = (0, 0, 0, 4)
                    imagem_static.styles.background = "0%"
                    self.query_one("#vs_mensagens", VerticalScroll).mount(
                        stt_nome_autor, imagem_static)
            case "audio":
                for audio_exibidos in self.query_one("#vs_mensagens", VerticalScroll).query(Audio.Audio):
                    if audio_exibidos.name == data["hash"]:
                        encontrado = True
                        break
                if not encontrado:
                    bar = Audio.Audio(arquivo, data["nome"], name=data["hash"])
                    self.query_one("#vs_mensagens", VerticalScroll).mount(
                        stt_nome_autor, bar)
            case "video":
                for videos_exibidos in self.query_one("#vs_mensagens", VerticalScroll).query(Video.Video):
                    if videos_exibidos.name == data["hash"]:
                        encontrado = True
                        break
                if not encontrado:
                    stt = Video.Video(
                        arquivo, name=data["hash"], pixel=True if self.app.servidor else False)
                    self.query_one("#vs_mensagens", VerticalScroll).mount(
                        stt_nome_autor, stt)
            case "documento":
                lista = list(self.query_one("#vs_mensagens",
                             VerticalScroll).query(Static))
                for stt_exibido in lista:
                    if stt_exibido.content.strip() == stt_nome_autor.content.strip():
                        index = lista.index(stt_exibido)
                        if index + 1 < len(lista):
                            depois = lista[index + 1]
                            if depois.name == data["hash"]:
                                encontrado = True
                                break
                        else:
                            break
                if not encontrado:
                    nome = data["nome"]
                    hash_val = data["hash"]
                    self.documentos[hash_val] = arquivo
                    self.query_one("#vs_mensagens", VerticalScroll).mount(stt_nome_autor, Static(
                        f"[@click=app.pdf('{hash_val}'))]{nome}[/]",
                        name=hash_val
                    ))
            case "mensagem":
                mensagem = Static(str(arquivo))
                lista = list(self.query_one(
                    "#vs_mensagens", VerticalScroll).query(Static))
                for stt_exibido in lista:
                    if stt_exibido.content.strip() == stt_nome_autor.content.strip():
                        index = lista.index(stt_exibido)
                        if index + 1 < len(lista):
                            depois = lista[index + 1]
                            if isinstance(depois.content, str):
                                if depois.content.strip() == mensagem.content.strip():
                                    encontrado = True
                                    break
                            else:
                                break
                if not encontrado:
                    self.query_one("#vs_mensagens", VerticalScroll).mount(
                        stt_nome_autor, mensagem)

    def handle_video_frame(self, usuario, frame: io.BytesIO):
        try:
            container = self.query_one(ContainerLigacao)
        except:
            container = ContainerLigacao()
            self.mount(container)
        try:
            camera = None
            for vertical in container.query_one("#cameras").query(Vertical):
                camera_procurando = vertical.query_one(
                    HalfcellImage if self.app.servidor else SixelImage)
                if camera_procurando and camera_procurando.name == usuario:
                    camera = camera_procurando
                    break
            if not camera:
                vt = Vertical()
                container.query_one("#cameras").mount(vt)
                camera = HalfcellImage(
                    pixel=True, name=usuario) if self.app.servidor else SixelImage(frame, name=usuario)
                camera.image = frame
                vt.mount(camera)
                vt.mount(Static(usuario.capitalize()))
            else:
                camera.image = frame
        except Exception as e:
            print(f"Erro em handle_video_frame: {e}")

    def handle_user_update(self, data):
        self.atualizar_lista_users(self.listar_usuarios())

    async def on_file_drop_dropped(self, event: FileDrop.Dropped) -> None:
        try:
            nome = "".join(event.filenames[-1])
            ext = nome[nome.index("."):].lower()
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
                    self.usuario.set_foto(blob)
                    self.banco.atualizar(
                        "Usuario", "foto", "cor", blob, self.usuario.get_cor())
                    await self.send_user_update()
                    self.notify("Foto de perfil atualizada!")
                else:
                    self.notify("ERRO: Arquivo não é imagem!")
                self.filedrop_perfil = False
            else:
                hash_val = hash(blob)
                dados = {
                    "autor": self.usuario.get_nome(),
                    "tipo": tipo,
                    "arquivo": base64.b64encode(blob).decode(),
                    "nome": nome,
                    "hash": hash_val
                }
                if self.ws:
                    await self.ws.send(json.dumps(["message", dados]))
            self.query_one(FileDrop).remove()
        except Exception as e:
            self.notify(str(e))

    async def on_button_pressed(self, event: Button.Pressed):
        input_widget = self.query_one(TextArea)
        match event.button.id:
            case "bt_filedrop":
                try:
                    self.query_one(FileDrop).remove()
                except:
                    self.mount(FileDrop())
            case "gravar":
                if not self.is_recording:
                    if self.ws:
                        await self.ws.send(json.dumps(["action", "audio"]))
                    self.query_one("#gravar", Button).label = "⬛"
                    self.query_one(TextArea).disabled = True
                    self.query_one(TextArea).text = "▶• Gravando..."
                    self.is_recording = True
                else:
                    if self.ws:
                        await self.ws.send(json.dumps(["action", "stop_audio"]))
                    self.query_one("#gravar", Button).label = "🔴"
                    self.query_one(TextArea).disabled = False
                    self.query_one(TextArea).text = ""
            case _:
                if input_widget.text:
                    dados = {
                        "autor": self.usuario.get_nome(),
                        "tipo": "mensagem",
                        "arquivo": input_widget.text,
                        "hash": "",
                        "nome": ""
                    }
                    if self.ws:
                        await self.ws.send(json.dumps(["message", dados]))
                    input_widget.text = ""

    async def on_click(self, event: Click):
        if event.widget.parent.parent.id == "lv_usuarios":
            if isinstance(event.widget, Static) and "📞" in event.widget.content:
                receiver = event.widget.content[4:-2]
                dados = {"caller": self.usuario.get_nome(),
                         "receiver": receiver}
                if self.ws:
                    await self.ws.send(json.dumps(["call", dados]))
            elif isinstance(event.widget, Static) and "👤" in event.widget.content:
                try:
                    self.query_one(FileDrop).remove()
                    self.filedrop_perfil = False
                except:
                    self.mount(FileDrop())
                    self.query_one(FileDrop).focus()
                    self.filedrop_perfil = True

    def pdf(self, hash_val):
        self.app.action_pdf(hash_val)

    def listar_usuarios(self):
        if self.usuario.get_nome() != "":
            agora = int(time.time())
            usuarios = self.banco.carregar_usuarios() or list()
            ativos = {}
            for usuario in usuarios:
                if agora - usuario.get_tempo() <= 60:
                    ativos[f"👤 🟢 {usuario.get_nome()} 📞"] = usuario
                else:
                    ativos[f"👤 🔴 {usuario.get_nome()}"] = usuario
            return ativos

    def atualizar_lista_users(self, users):
        lista = self.query_one("#lv_usuarios", ListView)
        lista.remove_children()
        lista.append(Static("Usuários:"))

        if users:
            for chave, user in users.items():
                nome_user = Static(chave)
                if user.get_cor():
                    nome_user.styles.color = user.get_cor()

                if user.get_foto():
                    lst_item = ListItem()
                    lst_item.styles.layout = "horizontal"
                    lista.append(lst_item)
                    if self.app.servidor == True:
                        imagem_static = HalfcellImage(io.BytesIO(
                            user.get_foto()), id="stt_foto_perfil")
                    else:
                        imagem_static = SixelImage(io.BytesIO(
                            user.get_foto()), id="stt_foto_perfil")

                    imagem_static.styles.width = 5
                    imagem_static.styles.height = 5
                    imagem_static.styles.background = "0%"
                    lst_item.mount(imagem_static, nome_user)
                else:
                    lista.append(ListItem(nome_user))
