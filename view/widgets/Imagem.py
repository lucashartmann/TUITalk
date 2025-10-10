from rich_pixels import Pixels
from PIL import Image
from textual.widgets import Static
import io
from textual import on

class Imagem(Static):
    
    def __init__(self, imagem, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.imagem = imagem
        if isinstance(imagem, bytes):
            self.img = Image.open(io.BytesIO(imagem))
        else:
            self.img = Image.open(imagem)
      
    def on_mount(self):
        pixels = Pixels.from_image(self.img, resize=(30,30))
        self.update(pixels)   

    def notify_style_update(self):
        if self.size.width and self.size.height:
            pixels = Pixels.from_image(self.img, resize=(self.size.width, int(self.size.height*2)))
            self.update(pixels)   