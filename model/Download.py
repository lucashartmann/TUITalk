import os
import io
import tempfile
import wave
import requests
from urllib.parse import urlparse, parse_qs
from pydub import AudioSegment
import yt_dlp


def baixar_para_memoria_ou_temp(url: str):
    if "youtube" in url or "youtu.be" in url:
        return baixar_youtube(url)
    elif "drive.google.com" in url:
        return baixar_drive(url)

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    resp = requests.get(url, stream=True, timeout=30, headers=headers)
    if resp.status_code == 403:
        return {"error": "403 Forbidden. Tente usar outro Referer/User-Agent ou baixar manualmente."}
    resp.raise_for_status()

    nome = os.path.basename(url.split("?")[0]) or "download"
    ext = os.path.splitext(nome)[1].lower()
    ctype = resp.headers.get("Content-Type", "")

    fotos = ext in (".jpg", ".jpeg", ".png", ".gif", ".webp",
                    ".bmp", ".tiff") or ctype.startswith("image/")
    videos = ext in (".mp4", ".mov", ".avi", ".mkv", ".webm",
                     ".flv") or ctype.startswith("video/")
    audios = ext in (".mp3", ".wav", ".ogg", ".flac", ".m4a",
                     ".aac") or ctype.startswith("audio/")

    content = io.BytesIO()
    for chunk in resp.iter_content(chunk_size=8192):
        if chunk:
            content.write(chunk)
    content.seek(0)

    tipo = "documento"

    try:
        if audios:
            tipo = "audio"
            if ext == ".wav" or ctype == "audio/wav":
                arquivo = wave.open(content, "rb")
            else:
                fmt = ext.lstrip(".") if ext else None
                content.seek(0)
                arquivo = AudioSegment.from_file(content, format=fmt or "mp3")
        elif fotos:
            tipo = "imagem"
            arquivo = content
        elif videos:
            tipo = "video"
            arquivo = content
        else:
            tipo = "documento"
            arquivo = content

        return {"arquivo": arquivo, "tipo": tipo, "nome": nome}

    except Exception as e:
        return {"error": str(e), "tipo": "erro", "nome": nome}


def baixar_youtube(url: str, prefer_audio=False, audio_format="mp3"):
    with tempfile.TemporaryDirectory() as tmpdir:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "outtmpl": os.path.join(tmpdir, "%(id)s.%(ext)s"),
            "noplaylist": True,
        }

        if prefer_audio:
            ydl_opts.update({
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": audio_format,
                    "preferredquality": "192",
                }],
            })
        else:
            ydl_opts.update({
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if prefer_audio:
                base, _ = os.path.splitext(filename)
                filename = base + f".{audio_format}"

        with open(filename, "rb") as f:
            data = f.read()
        os.remove(filename)

        nome = os.path.basename(filename)
        ext = os.path.splitext(filename)[1].lower()
        blob = io.BytesIO(data)
        blob.seek(0)

        tipo = "audio" if prefer_audio else "video"
        return {"arquivo": blob, "tipo": tipo, "nome": nome}


def baixar_drive(url: str):
    file_id = None
    if "/d/" in url:
        file_id = url.split("/d/")[1].split("/")[0]
    else:
        qs = parse_qs(urlparse(url).query)
        file_id = qs.get("id", [None])[0]

    if not file_id:
        raise ValueError("Não consegui extrair o ID do Google Drive")

    session = requests.Session()
    URL = "https://docs.google.com/uc?export=download"
    response = session.get(URL, params={"id": file_id}, stream=True)

    token = None
    for k, v in response.cookies.items():
        if k.startswith("download_warning"):
            token = v
            break
    if token:
        response = session.get(
            URL, params={"id": file_id, "confirm": token}, stream=True)

    nome = response.headers.get("Content-Disposition")
    if nome:
        import re
        m = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)"?', nome)
        nome = m.group(1) if m else f"{file_id}.bin"
    else:
        nome = f"{file_id}.bin"

    ctype = response.headers.get("Content-Type", "").lower()
    ext = os.path.splitext(nome)[1].lower()
    if ctype.startswith("image/") or ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        tipo = "imagem"
    elif ctype.startswith("video/") or ext in [".mp4", ".mov", ".avi", ".mkv", ".webm"]:
        tipo = "video"
    elif ctype.startswith("audio/") or ext in [".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac"]:
        tipo = "audio"
    else:
        tipo = "documento"

    content = io.BytesIO()
    for chunk in response.iter_content(32768):
        if chunk:
            content.write(chunk)
    content.seek(0)

    return {"arquivo": content, "tipo": tipo, "nome": nome}
