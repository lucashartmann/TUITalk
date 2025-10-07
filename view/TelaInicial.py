from pydub import AudioSegment
from view.widgets import Audio, Video, Imagem
from textual_filedrop import FileDrop
from textual_filedrop import getfiles
from view.widgets import ChamadaVideo, Video
from rich_pixels import Pixels
from view.widgets import Audio, Video, Imagem, ChamadaVideo
import tempfile
import time
import wave
import io

from textual.screen import Screen
from textual.widgets import Input, TextArea, Button, Static, ListItem, ListView, Header, Footer
from textual.containers import HorizontalScroll, VerticalScroll, HorizontalGroup, Container
from textual.timer import Timer
from textual.events import Click

from textual_image.widget import Image

from database import Banco
from model import Download, Usuario

class TelaInicial(Screen):
    CSS_PATH = "css/TelaInicial.tcss"

    mensagens = list()
    _poll_timer: Timer = None
    resultado = ""

    atendeu = False
    montou_container_foto = False
    usuario = Usuario.Usuario()

    def compose(self):
        yield Header()
        with HorizontalScroll():
            yield ListView(id="lv_grupos")
            with VerticalScroll():
                yield VerticalScroll(id="vs_mensagens")
                with HorizontalGroup():
                    yield TextArea(placeholder="Digite aqui")
                    yield Button("Enviar", id="bt_enviar_mensagem")
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

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        input_widget = self.query_one(TextArea)

        match event.button.id:
            case "gravar":
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

            case "bt_ligacao_true" | "bt_ligacao_false":
                await self.query_one("#container_call", Container).remove()
                Banco.deletar("banco.db", "chamada")
                Banco.salvar("banco.db", "chamata_atendida", False)
                if event.button.id == "bt_ligacao_true":
                    self.atendeu = True
                    Banco.salvar("banco.db", "chamata_atendida", True)
                    self.ligacao()

            case "bt_ligacao_true" | "bt_ligacao_false":
                await self.query_one("#container_call", Container).remove()
                Banco.deletar("banco.db", "chamada")
                Banco.salvar("banco.db", "chamada_atentida", False)
                if event.button.id == "bt_ligacao_true":
                    self.atendeu = True
                    Banco.salvar("banco.db", "chamada_atentida", True)
                self.ligacao()

            case _:

                if input_widget.text:
                    if self.montou_container_foto:
                        try:
                            input_widget = self.query_one(Input)
                            dados = Download.baixar_para_memoria_ou_temp(
                                input_widget.value)
                            if dados:
                                imagem_static = Image(dados["arquivo"])
                                imagem_static.styles.width = 30
                                imagem_static.styles.height = 30
                                container = self.get_child_by_id(
                                    "container_foto")
                                container.mount(imagem_static, before=0)
                                imagem_static.styles.width = 5
                                imagem_static.styles.height = 5
                                self.usuario.set_pixel_perfil(imagem_static)
                                carregar_users = Banco.carregar(
                                    "banco.db", "usuarios")
                                carregar_users[self.usuario.get_nome()
                                               ] = self.usuario
                                Banco.salvar(
                                    "banco.db", "usuarios", carregar_users)
                            else:
                                raise Exception
                        except Exception as e:
                            self.notify(f"ERRO! {e}")

                    elif "http" in input_widget.text or "https" in input_widget.text:
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
                        nome_user_static = Static(
                            self.usuario.get_nome(), classes="stt_usuario")
                        if self.usuario.get_cor():
                            nome_user_static.styles.color = self.usuario.get_cor()

                        nova_mensagem = Static(str(input_widget.text))
                        self.mensagens.append(
                            {"autor": self.usuario.get_nome(), "mensagem": str(input_widget.text)})

                        Banco.salvar("banco.db", "mensagens", self.mensagens)

                        self.query_one("#vs_mensagens", VerticalScroll).mount(
                            nome_user_static, nova_mensagem)

    def on_click(self, evento: Click):

        # if str(evento.widget) == "HeaderTitle()":
        #     if self.montou_container_foto:
        #         container = self.get_child_by_id("container_foto")
        #         container.remove()
        #         self.montou_container_foto = False

        if evento.widget.parent.parent.id == "lv_usuarios":
            if isinstance(evento.widget, Static) and not isinstance(evento.widget, Pixels) and not isinstance(evento.widget.content, Pixels):
                if "📞" in evento.widget.content:
                    Banco.salvar("banco.db", "chamada", {
                        self.usuario.get_nome(): evento.widget.content[2:-2]})

                elif "👤" in evento.widget.content:

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

        input_widget = self.query_one(TextArea)

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
                    nome_user_static = Static(
                        self.usuario.get_nome(), classes="stt_usuario")
                    if self.usuario.get_cor():
                        nome_user_static.styles.color = self.usuario.get_cor()

                    nova_mensagem = Static(str(input_widget.text))
                    self.mensagens.append(
                        {"autor": self.usuario.get_nome(), "mensagem": str(input_widget.text)})

                    Banco.salvar("banco.db", "mensagens", self.mensagens)

                    self.query_one("#vs_mensagens", VerticalScroll).mount(
                        nome_user_static, nova_mensagem)

            input_widget.clear()

    def on_click(self, evento: Click):

        # if str(evento.widget) == "HeaderTitle()":
        #     if self.montou_container_foto:
        #         container = self.get_child_by_id("container_foto")
        #         container.remove()
        #         self.montou_container_foto = False

        if isinstance(evento.widget, Static) and not isinstance(evento.widget, Pixels) and not isinstance(evento.widget.content, Pixels):
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

    montou_ligacao = False
    montou_caller = False

    def salvar(self, frame):

        chamada_em_curso = Banco.carregar(
            "banco.db", "chamada_em_curso")
        chamada_em_curso[self.usuario.get_nome()] = frame
        Banco.salvar("banco.db", "chamada_em_curso", chamada_em_curso)

    def ligacao(self):

        if self.montou_ligacao:
            container = self.get_child_by_id(
                "container_ligacao_em_curso")

            chamada_em_curso = Banco.carregar(
                "banco.db", "chamada_em_curso")

            if len(chamada_em_curso) > 1:

                for usuario, frame in chamada_em_curso.items():
                    if usuario != self.usuario.get_nome():
                        caller = usuario
                        frame = frame
                        break

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
            stt_video = ChamadaVideo.Caller(id=self.usuario.get_nome())
            stt_video.nome_user = self.usuario.get_nome()
            container.mount(stt_video)
            self.montou_ligacao = True

        # se a pessoa clicou para desligar a ligação aí faz self.montou_ligacao = False, self.atendeu = False

    montou_notificacao = False

    def poll_dados(self):
        if self.nome_user != "":

            chamada = Banco.carregar("banco.db", "chamada")
            if chamada:
                if self.usuario.get_nome() in chamada.values() and not self.montou_notificacao:
                    container = Container(id="container_call")
                    self.mount(container)
                    container.mount(
                        Static(F"{chamada.keys()} está te ligando! Aceitar?"))
                    container.mount(Button("Sim", id="bt_ligacao_true"))
                    container.mount(Button("Não", id="bt_ligacao_false"))
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
                    lst_item.mount(Static(user.get_pixel_perfil()), nome_user)
                else:
                    lista.append(ListItem(nome_user))
