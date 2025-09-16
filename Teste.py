from textual.app import App, ComposeResult
from textual.widgets import Button, Label
import sounddevice as sd
import wave
import numpy as np


class ChatVoz(App):
    CSS = "Button { margin: 1; }"

    def __init__(self):
        super().__init__()
        self.fs = 44100
        self.is_recording = False
        self.frames = []

    def compose(self) -> ComposeResult:
        yield Label("Chat com Áudio")
        yield Button("🎙️ Gravar / Parar", id="gravar")
        yield Button("▶️ Reproduzir", id="play")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "gravar":
            if not self.is_recording:
                self.start_recording()
            else:
                self.stop_recording()
        elif event.button.id == "play":
            self.play_audio()

    def start_recording(self):
        self.is_recording = True
        self.frames = []
        self.query_one(Label).update("🔴 Gravando...")

        def callback(indata, frames, time, status):
            if self.is_recording:
                self.frames.append(indata.copy())

        self.stream = sd.InputStream(samplerate=self.fs, channels=1, callback=callback)
        self.stream.start()

    def stop_recording(self):
        self.is_recording = False
        self.stream.stop()
        self.stream.close()

        audio = np.concatenate(self.frames, axis=0)
        with wave.open("mensagem.wav", "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16 bits
            wf.setframerate(self.fs)
            wf.writeframes((audio * 32767).astype(np.int16).tobytes())

        self.query_one(Label).update("✅ Mensagem salva em mensagem.wav")

    def play_audio(self):
        try:
            with wave.open("mensagem.wav", "rb") as wf:
                data = wf.readframes(wf.getnframes())
                audio = np.frombuffer(data, dtype=np.int16)
                sd.play(audio, samplerate=self.fs)
                sd.wait()
            self.query_one(Label).update("▶️ Reproduzido!")
        except FileNotFoundError:
            self.query_one(Label).update("❌ Nenhum áudio gravado ainda")


if __name__ == "__main__":
    ChatVoz().run()