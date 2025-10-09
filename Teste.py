from textual.app import App
from textual.widgets import Input, TextArea, Button, Static, ListItem, ListView, Header, Footer
from textual.containers import HorizontalScroll, VerticalScroll, Horizontal, HorizontalGroup, Container
from view.widgets import Audio, Video, Imagem, ChamadaVideo
from textual_image.widget import Image
from model import Download, Usuario


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
        self.screen.montou_container_foto = False
        self.remove()


class ContainerLigacao(Container):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_mount(self):
        self.styles.layer = "above"


    def compose(self):
        with Horizontal():
            yield Button("❌")
            yield Static("ᑕᕼᗩᗰᗩᗪᗩ", id="titulo")
        with HorizontalGroup():
            pass
            

    def on_button_pressed(self):
        self.remove()


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


class App(App):
    CSS_PATH = "view/css/TelaInicial.tcss"


    def on_mount(self):
        self.ligacao()

    def ligacao(self):
            container = ContainerLigacao()
            self.mount(container)
            stt_video = ChamadaVideo.Call(
                id="Lucas", pixel=True)
            container.query_one(HorizontalGroup).mount(stt_video)
   
           
            receiver = ChamadaVideo.Call(id="pedro", pixel=True)
            container.query_one(HorizontalGroup).mount(receiver)

App().run()