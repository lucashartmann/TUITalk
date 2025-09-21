import sounddevice as sd
import wave
import numpy as np
from pydub import AudioSegment
import os


class ChatVoz:

    def __init__(self):
        super().__init__()
        self.fs = 44100
        self.is_recording = False
        self.is_playing = False
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

    def stop_recording(self, salvar_path="mensagem.wav"):
        self.is_recording = False
        self.stream.stop()
        self.stream.close()

        audio = np.concatenate(self.frames, axis=0)
        with wave.open(salvar_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.fs)
            wf.writeframes((audio * 32767).astype(np.int16).tobytes())


    def tocar_audio(self, audio_segment):
        if self.is_playing:
            sd.stop()
            self.is_playing = False
            return
        
        if isinstance(audio_segment, AudioSegment):
            samples = np.array(audio_segment.get_array_of_samples())
            if audio_segment.channels == 2:
                samples = samples.reshape((-1, 2))
            sd.play(samples, samplerate=audio_segment.frame_rate)
            self.is_playing = True

        elif isinstance(audio_segment, wave.Wave_read):
            data = audio_segment.readframes(audio_segment.getnframes())
            audio = np.frombuffer(data, dtype=np.int16)
            sd.play(audio, samplerate=audio_segment.getframerate())
            self.is_playing = True


       