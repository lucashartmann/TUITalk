import cv2
from PIL import Image
from rich_pixels import Pixels
from textual.widgets import Static
from textual.timer import Timer


class Caller(Static):
    def __init__(self, pixel=True, *args, **kwargs):
        super().__init__(**kwargs)
        self.cap = None
        self.timer: Timer | None = None
        self.width = 30
        self.height = 30
        self.nome_user = ""
        self.pixel = pixel

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

        if self.pixel:
            pixels = Pixels.from_image(img)
            self.update(pixels)
        # else:
        #     self.query_one(TextualImage).image = img

    def on_unmount(self):
        if self.timer:
            self.timer.stop()
        if self.cap and self.cap.isOpened():
            self.cap.release()


class Receiver(Static):
    def __init__(self, pixel=True, *args, **kwargs):
        super().__init__(**kwargs)
        self.cap = None
        self.timer: Timer | None = None
        self.width = 30
        self.height = 30
        self.nome_user = ""
        self.pixel = pixel

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

    def update_frame(self, frame_rgb):
        img = Image.fromarray(frame_rgb)

        img = self.resize_image(img)
        if img is None:
            return

        if self.pixel:
            pixels = Pixels.from_image(img)
            self.update(pixels)
        # else:
        #     self.query_one(TextualImage).image = img

    def on_unmount(self):
        if self.timer:
            self.timer.stop()
        if self.cap and self.cap.isOpened():
            self.cap.release()
