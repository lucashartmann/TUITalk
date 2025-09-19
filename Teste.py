import cv2
import sys
import time
from PIL import Image
from rich.console import Console
from rich_pixels import Pixels
from rich.live import Live

def play_video(video):
    console = Console()
    cap = cv2.VideoCapture(video)

    fps = 60
    delay = 1 / min(fps, 15)  # limita FPS pra não travar o terminal

    with Live(console=console, screen=True, refresh_per_second=15) as live:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # OpenCV lê em BGR, converte pra RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)

            # Redimensiona pra caber no terminal
            img = img.resize((120, 100))

            # Mostra o frame
            pixels = Pixels.from_image(img)
            live.update(pixels)

            time.sleep(delay)

    cap.release()
