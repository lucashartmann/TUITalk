from textual.app import App
from textual.widgets import Input, TextArea, Button, Static, ListItem, ListView, Header, Footer
from textual.containers import HorizontalScroll, VerticalScroll, Horizontal, HorizontalGroup, Container
from view.widgets import Audio, Video, Imagem, ChamadaVideo
from textual_image.widget import Image
from model import Download, Usuario
from PIL import Image as PILImage


class ContainerFoto(Container):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_mount(self):
        self.styles.layer = "above"
        self.mount(Imagem.Imagem(r"C:\Users\LUCASAUGUSTOHARTMANN\Downloads\SpongeBob_SquarePants_personagem.png",
                   id="stt_foto_perfil"), before=self.query_one(Input))

    def compose(self):
        yield Button("❌")
        yield Input(placeholder="caminho da foto")
        yield Button("Enviar", id="enviar")

    def on_button_pressed(self, evento: Button.Pressed):
        self.remove()


class App(App):
    CSS_PATH = "view/css/TelaInicial.tcss"

    def compose(self):
        yield ContainerFoto()


App().run()
