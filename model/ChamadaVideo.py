import cv2
from PIL import Image
from rich_pixels import Pixels
from textual.widgets import Static
from textual.timer import Timer
from database import Banco

class VideoWidget(Static):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cap = None
        self.timer: Timer | None = None
        self.width = 30
        self.height = 30
        self.nome_user = ""

    def on_mount(self) -> None:
        self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            self.update("Could not open camera")
            return

        self.timer = self.set_interval(1/15, self.update_frame)

    def resize_image(self, image: Image.Image):
        size = (self.width, self.height)
        try:
            image.thumbnail(size, Image.Resampling.LANCZOS)
        except ValueError:
            return None
        return image

    def update_frame(self):
        if not self.cap or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if not ret:
            self.update("Could not read frame")
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)

        img = self.resize_image(img)
        if img is None:
            return

        pixels = Pixels.from_image(img)
        self.update(pixels)
        
        Banco.salvar("banco.db", "chamada_em_curso", {self.nome_user : frame_rgb})

    def on_unmount(self):
        if self.timer:
            self.timer.stop()
        if self.cap and self.cap.isOpened():
            self.cap.release()

