from textual.widgets import Static


class VideoWidget(Static):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.video_stream = None

    def update_frame(self, frame):
        pass