from rich_pixels import Pixels
from PIL import Image
import os


def resize(caminho):
    size = 30, 30

    if not os.path.exists(caminho):
        print(f"Imagem não encontrada: {caminho}")
        return False, ""

    try:
        im = Image.open(caminho)
        im.thumbnail(size, Image.Resampling.LANCZOS)
        novo_caminho = f"{caminho.split('.')[0]}copia.{caminho.split('.')[1]}"
        im.save(novo_caminho)
        if os.path.exists(novo_caminho):
            os.remove(novo_caminho)
    except ValueError:
        return None
    return im


def gerar_pixel(imagem):
    try:
        pixels = Pixels.from_image(imagem)
        return pixels
    except Exception:
        print(f"Erro ao gerar pixels")
        return None
