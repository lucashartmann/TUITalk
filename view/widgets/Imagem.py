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
        print("size.width", self.size.width)
        print("styles.width", self.styles.width)
        pixels = Pixels.from_image(self.img, resize=(self.styles.width,self.styles.height))
        self.update(pixels)   