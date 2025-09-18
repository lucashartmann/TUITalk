import sounddevice as sd
import wave
import numpy as np


class ChatVoz():

    def __init__(self):
        super().__init__()
        self.fs = 44100
        self.is_recording = False
        self.frames = []

    def start_recording(self):
        self.is_recording = True
        self.frames = []

        def callback(indata, frames, time, status):
            if self.is_recording:
                self.frames.append(indata.copy())

        self.stream = sd.InputStream(
            samplerate=self.fs, channels=1, callback=callback)
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

    def tocar_audio(self, arquivo):
            wf = arquivo
            data = wf.readframes(wf.getnframes())
            audio = np.frombuffer(data, dtype=np.int16)
            sd.play(audio, samplerate=wf.getframerate())
            sd.wait()

    def play_audio(self):
        try:
            with wave.open("mensagem.wav", "rb") as wf:
                data = wf.readframes(wf.getnframes())
                audio = np.frombuffer(data, dtype=np.int16)
                sd.play(audio, samplerate=wf.getframerate())
                sd.wait()
        except FileNotFoundError:
            pass
