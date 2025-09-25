import cv2
from PIL import Image
from rich_pixels import Pixels
from textual.widgets import Static


class Video(Static):
    def __init__(self, video, width: int = 30, height: int = 30):
        super().__init__()
        self.cap = cv2.VideoCapture(video)
        self.width = width
        self.height = height


    def on_mount(self) -> None:
        self.set_interval(1 / 15, self.update_frame)

    def resizeImagem(self, imagem: Image.Image) -> Image.Image | None:
        size = (self.width, self.height)
        try:
            imagem.thumbnail(size, Image.Resampling.LANCZOS)
        except ValueError:
            return None
        return imagem

    def update_frame(self) -> None:
        if not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if not ret:
            self.cap.release()
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)

        img = self.resizeImagem(img)
        if img is None:
            return

        pixels = Pixels.from_image(img)
        self.update(pixels)
