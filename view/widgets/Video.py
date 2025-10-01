import cv2
from PIL import Image
from textual.widget import Widget
from textual.widgets import Button
from textual_image.widget import Image as TextualImage
from textual.timer import Timer


class Video(Widget):

    def __init__(self, video_path, width=30, height=10):
        super().__init__()
        self.cap = cv2.VideoCapture(video_path)
        self.width = width
        self.height = height
        self.timer: Timer | None = None
        self.paused = False

        ret, frame = self.cap.read()
        if not ret:
            raise ValueError("Não consegui abrir o vídeo")

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.pil_img = Image.fromarray(frame).resize((width, height))

        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 15
        self.interval = 1 / self.fps
        self.prev_frame = None

    def compose(self):
        yield TextualImage(self.pil_img)
        yield Button("▶️")

    def on_button_pressed(self):
        self.pause()

    def on_mount(self):
        self.styles.width = self.width
        self.styles.height = self.height
        self.query_one(TextualImage).styles.width = self.width
        self.query_one(TextualImage).styles.height = self.height
        self.query_one(Button).styles.align = ("center", "middle")
        self.query_one(Button).styles.height = 3
        self.query_one(Button).styles.width = self.width

    def start(self):
        self.timer = self.set_interval(1/30, self.update_frame)

    def pause(self):
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
        if not self.cap.isOpened():
            return False

        ret, frame = self.cap.read()
        if not ret:
            self.cap.release()
            return False

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = frame.astype("uint8")

        if frame.shape[2] == 4:
            frame = frame[:, :, :3]

        img = Image.fromarray(frame)

        if img:
            if self.prev_frame is None or not (self.prev_frame.tobytes() == img.tobytes()):
                self.query_one(TextualImage).image = img
                self.prev_frame = img
        return True
