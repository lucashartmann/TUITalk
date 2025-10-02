from rich_pixels import Pixels
from PIL import Image
from textual.widgets import Static
import io

class Imagem(Static):
    
    def __init__(self, imagem, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.imagem = imagem
        if isinstance(imagem, bytes):
            img = Image.open(io.BytesIO(imagem))
        else:
            img = Image.open(imagem)
            
        pixels = Pixels.from_image(img, resize=(33, 30))
        self.update(pixels)       
        

    