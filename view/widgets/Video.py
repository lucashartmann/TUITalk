import cv2
from PIL import Image
from textual.widget import Widget
from textual.widgets import Button, Static
from textual_image.widget import Image as TextualImage
from textual.timer import Timer
from textual.containers import VerticalGroup
import hashlib
from rich_pixels import Pixels

class Video(Widget):

    def __init__(self, video_path, pixel=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.captura_video = cv2.VideoCapture(video_path)
        self.timer: Timer | None = None
        self.paused = False
        self.pixel = pixel

        leu_frame, frame = self.captura_video.read()
        if not leu_frame:
            raise ValueError("Não consegui abrir o vídeo")

        self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.pil_img = Image.fromarray(frame)

        self.fps = self.captura_video.get(cv2.CAP_PROP_FPS) or 15
        if self.fps < 15:  
            self.fps = 15
        self.interval = 1 / self.fps
        self.prev_frame = None

    def compose(self):
        with VerticalGroup(id="video_container"):
            if self.pixel == False:
                yield TextualImage(self.pil_img)
            else:
                yield Static(Pixels.from_image(self.pil_img), id="video_pixels")
            yield Button("▶️")
            
    def resizeImagem(self,size, imagem: Image.Image) -> Image.Image | None:
        try:
            if self.pixel:
                size = (size[0]*1.10, size[1]*1.50)
                imagem.thumbnail(size, Image.Resampling.LANCZOS)
            else:
                imagem.resize(size, Image.Resampling.LANCZOS)
        except ValueError:
            return None
        return imagem

    def on_button_pressed(self):
        self.pause()

        
    def start(self):
        self.timer = self.set_interval(1/15, self.update_frame)

    def pause(self):
        if not self.captura_video.isOpened():
            self.captura_video = cv2.VideoCapture(self.video_path)
        
        if not self.timer:
            self.start()
        else:
            if self.paused:
                self.timer.resume()
                self.paused = False
            else:
                self.timer.pause()
                self.paused = True

    def update_frame(self):
        if not self.captura_video.isOpened():
            return False

        leu_frame, frame = self.captura_video.read()
        if not leu_frame:
            self.captura_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return False

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        frame = frame.astype("uint8")

        if frame.shape[2] == 4:
            frame = frame[:, :, :3]


        img = Image.fromarray(frame)
        
        widget = self.query_one("#video_container")
        width = widget.size.width
        height = widget.size.height
        
        img = self.resizeImagem((width, height), img)

        if img:
            h = hashlib.md5(frame[::10, ::10].tobytes()).hexdigest()
            if self.prev_frame != h:
                if self.pixel:
                    pixels = Pixels.from_image(img)
                    self.query_one(Static).update(pixels)
                else:
                    self.query_one(TextualImage).image = img
                self.prev_frame = img
        return True
