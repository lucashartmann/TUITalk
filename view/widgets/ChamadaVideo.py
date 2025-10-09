import base64
import io
import cv2
from PIL import Image
from rich_pixels import Pixels
from textual.widgets import Static
from textual.timer import Timer


class Call(Static):
    def __init__(self, pixel=True, *args, **kwargs):
        super().__init__(**kwargs)
        self.width = 30
        self.height = 30
        self.nome_user = ""
        self.pixel = pixel
        
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
        
        if not frame or isinstance(frame, str):
            return
       
        try:
            img = Image.open(io.BytesIO(frame))
            
            img = self.resize_image(img)
            if img is None:
                return

            if self.pixel:
                pixels = Pixels.from_image(img)
                self.update(pixels)
        except Exception as e:
            print("ERRO update_frame:", e)
            return
        # else:
        #     self.query_one(TextualImage).image = img
