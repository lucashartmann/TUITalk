from rich_pixels import Pixels
from PIL import Image
from textual.widgets import Static
import io

class Imagem(Static):
    
    def __init__(self, imagem, width=41, height=16, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.width = width
        self.height = height
        self.styles.width = self.width
        self.styles.height = self.height
        self.imagem = imagem
        if isinstance(imagem, bytes):
            img = Image.open(io.BytesIO(imagem))
        else:
            img = Image.open(imagem)
            
        pixels = Pixels.from_image(img, resize=(self.width, self.height))
        self.update(pixels)       

    