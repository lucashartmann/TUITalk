from textual.widgets import Button
from textual.widget import Widget
from textual.containers import VerticalGroup
from textual_video.player import VideoPlayer
from textual_video.player import ImageType
import io

class Video(Widget):
    def __init__(self, video_path, pixel=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.video_path = io.BytesIO(video_path)
        self.pixel = pixel
        self.video_player = None

    def compose(self):
        with VerticalGroup(id="video_container"):
            if self.pixel == False:
                self.video_player = VideoPlayer(path=self.video_path)
                yield self.video_player
            else:
                self.video_player = VideoPlayer(
                    path=self.video_path, image_type=ImageType.HALFCELL)
                yield self.video_player
            yield Button("▶️", id="play_pause_button")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "play_pause_button":
            if self.video_player:
                if not self.video_player.paused:
                    self.video_player.pause()
                    event.button.label = "▶️"
                else:
                    self.video_player.play()
                    event.button.label = "⏸️"
