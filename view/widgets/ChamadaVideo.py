from PIL import Image
from rich_pixels import Pixels
from textual.widgets import Static


class Call(Static):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.width = 30
        self.height = 30
        self.nome_user = ""

    def on_mount(self):
        self.update("Sem câmera")

    def resize_image(self, image: Image.Image):
        size = (self.width, self.height)
        try:
            image.thumbnail(size, Image.Resampling.LANCZOS)
        except ValueError:
            return None
        return image

    def update_frame(self, frame):
        try:
           
            img = Image.open(frame)
            
            img = self.resize_image(img)
           
           
            pixels = Pixels.from_image(img)
            self.update(pixels)
      

        except Exception as e:
            print(f"ChamadaVideo.py update_frame: {e}")
            return
            