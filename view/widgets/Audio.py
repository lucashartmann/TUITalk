import threading
import time
import numpy as np
import sounddevice as sd
from pydub import AudioSegment
import wave
from textual.widgets import ProgressBar, Button
from textual.containers import Horizontal
from textual.widget import Widget

class Audio(Widget):
    def __init__(self, audio_segment, nome, *args, **kwargs):
        super().__init__()
        self.is_playing = False
        self.audio_segment = audio_segment
        self.duration = self.get_duration()
        self.current_time = 0  
        self._play_thread = None
        self.nome = nome
        self.progress = ProgressBar(total=100, show_eta=True, show_percentage=True)
        self.progress.styles.height = 3
        self.progress.styles.background = "green"
        self.button = Button("▶️")
        self.button.styles.height = 3
        self.styles.height = 3

    def get_duration(self):
        if isinstance(self.audio_segment, AudioSegment):
            return self.audio_segment.duration_seconds
        elif isinstance(self.audio_segment, wave.Wave_read):
            return self.audio_segment.getnframes() / self.audio_segment.getframerate()
        return 0

    def make_progress(self, progress_value):
        self.progress.update(progress=progress_value)

    def compose(self):
        yield Horizontal(
            self.progress,
            self.button

        )

    def on_button_pressed(self):
        self.tocar_audio()

    def tocar_audio(self):
        if self.is_playing:
            sd.stop()
            self.is_playing = False
            return

        self.is_playing = True
        if self._play_thread is None or not self._play_thread.is_alive():
            self._play_thread = threading.Thread(target=self.play_audio, daemon=True)
            self._play_thread.start()
            threading.Thread(target=self.update_progress, daemon=True).start()

    def play_audio(self):
        if isinstance(self.audio_segment, AudioSegment):
            restante = self.audio_segment[self.current_time*1000:]  # em ms
            samples = np.array(restante.get_array_of_samples())
            if restante.channels == 2:
                samples = samples.reshape((-1, 2))
            sd.play(samples, samplerate=restante.frame_rate)
            sd.wait()  
            self.is_playing = False
            self.current_time = 0  

        elif isinstance(self.audio_segment, wave.Wave_read):
            framerate = self.audio_segment.getframerate()
            start_frame = int(self.current_time * framerate)
            self.audio_segment.setpos(start_frame)
            data = self.audio_segment.readframes(self.audio_segment.getnframes() - start_frame)
            audio = np.frombuffer(data, dtype=np.int16)
            sd.play(audio, samplerate=framerate)
            sd.wait()
            self.is_playing = False
            self.current_time = 0

    def update_progress(self):
        start = time.time() - self.current_time
        while self.is_playing:
            self.current_time = time.time() - start
            progress_value = min(100, (self.current_time / self.duration) * 100)
            self.make_progress(progress_value)
            if progress_value >= 100:
                self.is_playing = False
            time.sleep(0.05)
