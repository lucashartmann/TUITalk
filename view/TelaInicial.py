import asyncio
import time
import wave
import io


from textual.screen import Screen
from textual.widgets import Input, TextArea, Button, Static, ListItem, ListView, Header, Footer
from textual.containers import HorizontalScroll, VerticalScroll, HorizontalGroup, Container
from textual.timer import Timer
from textual.events import Click

from textual_image.widget import Image
from textual_filedrop import FileDrop
from textual_filedrop import getfiles
import websockets

from database import Banco
from model import Download, Usuario
from view.widgets import Audio, Video, Imagem, ChamadaVideo

from pydub import AudioSegment
from rich_pixels import Pixels


class ContainerFoto(Container):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_mount(self):
        self.styles.layer = "above"

    def compose(self):
        yield Button("❌")
        yield Input(placeholder="caminho da foto")
        yield Button("Enviar", id="enviar")

    def on_button_pressed(self, evento: Button.Pressed):
        if evento.button.id == "enviar":
            try:
                input_widget = self.query_one(Input)
                dados = Download.baixar_para_memoria_ou_temp(
                    input_widget.value)
                if dados:
                    if self.screen.app.servidor == True:
                        imagem_static = Imagem.Imagem(
                            dados["arquivo"], id="stt_foto_perfil")
                    else:
                        imagem_static = Image(
                            dados["arquivo"], id="stt_foto_perfil")
                    container = self.screen.query_one(ContainerFoto)
                    container.mount(imagem_static, before=Input)
                    self.screen.usuario.set_pixel_perfil(dados["arquivo"])
                    carregar_users = Banco.carregar(
                        "banco.db", "usuarios")
                    carregar_users[self.screen.usuario.get_nome()
                                   ] = self.screen.usuario
                    Banco.salvar(
                        "banco.db", "usuarios", carregar_users)

                else:
                    raise Exception
            except Exception as e:
                self.screen.notify(f"ERRO! {e}")
            self.query(Input).value = ""
        else:
            self.screen.montou_container_foto = False
            self.remove()


class ContainerLigacao(Container):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_mount(self):
        self.styles.layer = "above"

    def compose(self):
        yield Button("❌")
        with HorizontalGroup():
            pass

    def on_button_pressed(self):
        self.remove()
        Banco.salvar("banco.db", "acao", "stop_video")
        self.screen.stop_receber_frames()
        self.screen.montou_ligacao = False
        self.screen.atendeu = False
        self.screen.montou_caller = False
        self.screen.montou_notificacao = False


class ContainerMessageLigacao(Container):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_mount(self):
        self.styles.layer = "above"

    def compose(self):
        yield Static(F"está te ligando! Aceitar?")
        yield Button("Sim", id="bt_ligacao_true")
        yield Button("Não", id="bt_ligacao_false")

    async def on_button_pressed(self, evento: Button.Pressed):
        await self.remove()
        Banco.deletar("banco.db", "chamada")
        Banco.salvar("banco.db", "chamada_atentida", False)
        if evento.button.id == "bt_ligacao_true":
            self.parent.atendeu = True
            Banco.salvar("banco.db", "chamada_atentida", True)


class TelaInicial(Screen):
    CSS_PATH = "css/TelaInicial.tcss"
    mensagens = list()
    _poll_timer: Timer = None
    resultado = ""
    frame_task = None
    running = True
    atendeu = False
    montou_container_foto = False
    usuario = Usuario.Usuario()
    url = Banco.carregar("ngrok.db", "url")
    frame_recebido = ""
    audio = Audio.Audio("")
    montou_ligacao = False
    montou_caller = False
    montou_notificacao = False

    async def receber_frames(self):
        nova_url = self.url.replace(
            "https://", "wss://").replace("http://", "ws://")
        while True:
            try:
                async with websockets.connect(nova_url) as ws:
                    while True:
                        blob = await ws.recv()
                        acao = Banco.carregar("banco.db", "acao")
                        if acao == "video":
                            self.frame_recebido = blob
                            chamada_em_curso = Banco.carregar(
                                "banco.db", "chamada_em_curso") or {}
                            chamada_em_curso[self.usuario.get_nome()] = blob
                            Banco.salvar(
                                "banco.db", "chamada_em_curso", chamada_em_curso)
            except Exception as e:
                print(f"Erro na conexão WebSocket: {e}")
                await asyncio.sleep(1)  

    def start_receber_frames(self):
        loop = asyncio.get_event_loop()
        self.frame_task = loop.create_task(self.receber_frames())

    def stop_receber_frames(self):
        self.running = False
        if self.frame_task:
            self.frame_task.cancel()

    async def on_mount(self):
        try:
            Banco.deletar("banco.db", "acao")
        except:
            pass
        try:
            Banco.deletar("banco.db", "chamada")
        except:
            pass
        try:
            Banco.deletar("banco.db", "chamada_atentida")
        except:
            pass

        self.montou_ligacao = False
        self.atendeu = False
        self.montou_caller = False
        self.montou_notificacao = False
        self.montou_container_foto = False

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
                    yield Button("🔴", id="gravar")
            yield ListView(id="lv_usuarios")
        yield Footer()

    def exibir_midia(self, dados):
        if dados:

            nome_user_static = Static(
                self.usuario.get_nome(), classes="stt_usuario")

            if self.usuario.get_cor():
                nome_user_static.styles.color = self.usuario.get_cor()

            match dados["tipo"]:

                case "imagem":
                    if self.app.servidor == True:
                        img = Imagem.Imagem(
                            imagem=dados["arquivo"], name=hash(dados["arquivo"]))
                    else:
                        img = Image(dados["arquivo"],
                                    name=hash(dados["arquivo"]))
                        img.styles.width = 38
                        img.styles.height = 10
                        img.styles.margin = (0, 0, 0, 3)

                    self.query_one("#vs_mensagens", VerticalScroll).mount(
                        nome_user_static, img)
                    self.mensagens.append(
                        {"autor": self.usuario.get_nome(), "imagem": dados["arquivo"], "id": hash(dados["arquivo"])})
                    Banco.salvar("banco.db", "mensagens",
                                 self.mensagens)

                case "audio":
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
                        {"autor": self.usuario.get_nome(), "audio": blob, "id": hash(dados["arquivo"]), "nome": dados["nome"]})

                    self.query_one("#vs_mensagens", VerticalScroll).mount(
                        nome_user_static, Audio.Audio(blob, nome=dados["nome"], name=hash(dados["arquivo"])))

                    Banco.salvar("banco.db", "mensagens",
                                 self.mensagens)

                case "video":
                    if self.app.servidor == True:
                        video = Video.Video(dados["_temp_path"], name=hash(
                            dados["arquivo"]), pixel=True)
                    else:
                        video = Video.Video(
                            dados["_temp_path"], name=hash(dados["arquivo"]))
                    self.query_one("#vs_mensagens", VerticalScroll).mount(
                        nome_user_static, video)
                    self.mensagens.append(
                        {"autor": self.usuario.get_nome(), "video": dados["_temp_path"], "id": hash(dados["arquivo"])})
                    Banco.salvar("banco.db", "mensagens",
                                 self.mensagens)

                case "documento":
                    self.query_one("#vs_mensagens", VerticalScroll).mount(nome_user_static, Static(
                        dados["nome"], name=hash(dados["arquivo"])))
                    self.mensagens.append(
                        {"autor": self.usuario.get_nome(), "documento": dados["arquivo"], "id": hash(dados["arquivo"])})
                    Banco.salvar("banco.db", "mensagens",
                                 self.mensagens)
                    # TODO: implementar self.query_one("#vs_mensagens", VerticalScroll).mount(nome_user_static, Static(nome_do_arquivo.extensao, name=hash(dados["arquivo"])))

    async def on_button_pressed(self, event: Button.Pressed):
        input_widget = self.query_one(TextArea)
        nome_user_static = Static(
            self.usuario.get_nome(), classes="stt_usuario")

        match event.button.id:
            case "gravar":
                if not self.audio.is_recording:
                    Banco.salvar("banco.db", "acao", "audio")
                    self.start_receber_frames()
                    self.query_one("#gravar", Button).label = "⬛"
                    self.query_one(TextArea).disabled = True
                    self.query_one(TextArea).text = "▶• Gravando..."
                    self.audio.start_recording()
                else:
                    Banco.salvar("banco.db", "acao", "stop_audio")
                    self.stop_receber_frames()
                    self.query_one("#gravar", Button).label = "🔴"
                    self.query_one(TextArea).disabled = False
                    self.query_one(TextArea).text = ""
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

                    self.mensagens.append(
                        {"autor": self.usuario.get_nome(), "audio": blob, "id": hash(arquivo), "nome": ""})

                    self.query_one("#vs_mensagens", VerticalScroll).mount(
                        nome_user_static, Audio.Audio(blob, name=hash(arquivo)))

                    Banco.salvar("banco.db", "mensagens",
                                 self.mensagens)

            case _:

                if input_widget.text:

                    if "http" in input_widget.text or "https" in input_widget.text:
                        try:
                            dados = Download.baixar_para_memoria_ou_temp(
                                input_widget.text)
                            if dados:
                                self.exibir_midia(dados)
                            else:
                                raise Exception
                        except Exception as e:
                            self.notify(f"ERRO! {e}")

                    else:

                        if self.usuario.get_cor():
                            nome_user_static.styles.color = self.usuario.get_cor()

                        nova_mensagem = Static(str(input_widget.text))
                        self.mensagens.append(
                            {"autor": self.usuario.get_nome(), "mensagem": str(input_widget.text)})

                        Banco.salvar("banco.db", "mensagens", self.mensagens)

                        self.query_one("#vs_mensagens", VerticalScroll).mount(
                            nome_user_static, nova_mensagem)

    def on_click(self, evento: Click):
        if evento.widget.parent.parent.id == "lv_usuarios":
            if isinstance(evento.widget, Static) and not isinstance(evento.widget, Pixels) and not isinstance(evento.widget.content, Pixels):
                if "📞" in evento.widget.content:
                    Banco.salvar("banco.db", "chamada", {
                        self.usuario.get_nome(): evento.widget.content[4:-2]})

                elif "👤" in evento.widget.content:
                    ctt_foto = ContainerFoto()
                    self.mount(ctt_foto)
                    self.montou_container_foto = True

                # else:
                #     documento = self.documentos[evento.widget.name]
                # TODO: abrir documento, ou abrir foto dele montou_container_foto

    def ligacao(self):
        if not self.montou_ligacao:
            return

        container = self.query_one(ContainerLigacao)
        minha_camera = container.query_one(
            HorizontalGroup).get_child_by_id(self.usuario.get_nome())
        minha_camera.update_frame(self.frame_recebido)

        chamada_em_curso = Banco.carregar("banco.db", "chamada_em_curso")
        if not chamada_em_curso:
            return

        try:
            for usuario, frame in chamada_em_curso.items():
                if usuario != self.usuario.get_nome():
                    caller = usuario
                    frame_caller = frame
                    break
            else:
                return

            if not self.montou_caller:
                if self.app.servidor:
                    receiver = ChamadaVideo.Call(id=caller, pixel=True)
                    receiver.update_frame(frame_caller)
                    container.query_one(HorizontalGroup).mount(receiver)
                    self.montou_caller = True
            else:
                camera_caller = container.query_one(
                    HorizontalGroup).get_child_by_id(caller)
                camera_caller.update_frame(frame_caller)

        except Exception as e:
            print(f"Erro em ligacao(): {e}")

        else:
            Banco.salvar("banco.db", "acao", "video")
            self.start_receber_frames()
            container = ContainerLigacao()
            self.mount(container)
            stt_video = ChamadaVideo.Call(
                id=self.usuario.get_nome(), pixel=True)
            stt_video.nome_user = self.usuario.get_nome()
            if self.frame_recebido:
                stt_video.update_frame(self.frame_recebido)
            container.query_one(HorizontalGroup).mount(stt_video)
            self.montou_ligacao = True

    def poll_dados(self):

        chamada = Banco.carregar("banco.db", "chamada")
        if chamada:
            if self.usuario.get_nome() in chamada.values() and self.montou_notificacao == False:
                container = ContainerMessageLigacao()
                self.mount(container)
                container.query_one(Static).update(
                    F"{chamada.keys()} está te ligando! Aceitar?")
                self.montou_notificacao = True

        chamada_atendida = Banco.carregar("banco.db", "chamada_atentida")
        if chamada_atendida:
            self.ligacao()

        self.atualizar_usuario()
        users = self.listar_usuarios()

        carregar_users = Banco.carregar("banco.db", "usuarios")
        if carregar_users:
            self.atualizar_lista_users(users)

        carregar_msgs = Banco.carregar("banco.db", "mensagens")

        if carregar_msgs:
            self.mensagens = carregar_msgs

            for mensagem in self.mensagens:
                encontrado = False

                stt_nome_autor = Static(
                    mensagem["autor"], classes="stt_usuario")
                if carregar_users[mensagem["autor"]].get_cor():
                    stt_nome_autor.styles.color = carregar_users[mensagem["autor"]].get_cor(
                    )

                if "imagem" in mensagem.keys():
                    if self.app.servidor == True:
                        for stt in self.query_one("#vs_mensagens", VerticalScroll).query(Static):
                            if isinstance(stt, Pixels) or isinstance(stt.content, Pixels):
                                if stt.name == mensagem["id"]:
                                    encontrado = True
                                    break
                    else:
                        for stt in self.query_one("#vs_mensagens", VerticalScroll).query(Image):
                            if stt.name == mensagem["id"]:
                                encontrado = True
                                break
                    if encontrado == False:
                        if self.app.servidor == True:
                            imagem_static = Imagem.Imagem(
                                mensagem["imagem"], name=mensagem["id"])
                        else:
                            imagem_static = Image(
                                mensagem["imagem"], name=mensagem["id"])
                            imagem_static.styles.width = 38
                            imagem_static.styles.height = 10
                            imagem_static.styles.margin = (0, 0, 0, 3)

                        self.query_one("#vs_mensagens", VerticalScroll).mount(
                            stt_nome_autor, imagem_static)

                elif "audio" in mensagem.keys():
                    for audio_exibidos in self.query_one("#vs_mensagens", VerticalScroll).query(Audio.Audio):
                        if audio_exibidos.name == mensagem["id"]:
                            encontrado = True
                            break

                    if encontrado == False:
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
                        bar = Audio.Audio(
                            audio, mensagem["nome"], name=mensagem["id"])
                        self.query_one("#vs_mensagens", VerticalScroll).mount(
                            stt_nome_autor, bar)

                elif "video" in mensagem.keys():
                    for videos_exibidos in self.query_one("#vs_mensagens", VerticalScroll).query(Video.Video):
                        if videos_exibidos.name == mensagem["id"]:
                            encontrado = True
                            break
                    if encontrado == False:
                        if self.app.servidor == True:
                            stt = Video.Video(
                                mensagem["video"], name=mensagem["id"], pixel=True)
                        else:
                            stt = Video.Video(
                                mensagem["video"], name=mensagem["id"])
                        self.query_one("#vs_mensagens", VerticalScroll).mount(
                            stt_nome_autor, stt)

                elif "documento" in mensagem.keys():
                    pass  # TODO: implementar

                else:
                    mensagem = Static(mensagem["mensagem"])
                    lista = list(self.query_one(
                        "#vs_mensagens", VerticalScroll).query(Static))
                    for stt_exibido in lista:
                        content = stt_exibido.content
                        if hasattr(content, 'strip') and isinstance(content, str) and not isinstance(stt_exibido.content, Pixels) and not isinstance(stt_exibido, Pixels):
                            stt_exibido_conteudo = content.strip()
                        else:
                            break

                        if not isinstance(stt_exibido.content, Pixels) and hasattr(stt_exibido.content, 'strip') and isinstance(stt_exibido.content, str):
                            stt_nome_autor_conteudo = stt_nome_autor.content.strip()
                        else:
                            break
                        if stt_exibido_conteudo == stt_nome_autor_conteudo:
                            index = lista.index(stt_exibido)
                            if index + 1 < len(lista):
                                depois = lista[index + 1]
                                if not isinstance(depois.content, Pixels) and hasattr(depois.content, 'strip') and isinstance(depois.content, str):
                                    if depois.content.strip() == mensagem.content.strip():
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
            usuarios = Banco.carregar("banco.db", "usuarios") or {}
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
        usuarios = Banco.carregar("banco.db", "usuarios")
        if self.usuario.get_nome() in usuarios.keys():
            usuarios[self.usuario.get_nome()].set_tempo(agora)
        else:
            self.usuario.set_tempo(agora)
            usuarios[self.usuario.get_nome()] = self.usuario
        Banco.salvar("banco.db", "usuarios", usuarios)

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
                        imagem_static = Imagem.Imagem(
                            user.get_pixel_perfil(), id="stt_foto_perfil")
                    else:
                        imagem_static = Image(
                            user.get_pixel_perfil(), id="stt_foto_perfil")
                    lst_item.mount(imagem_static, nome_user)
                else:
                    lista.append(ListItem(nome_user))
