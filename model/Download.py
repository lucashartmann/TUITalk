import os
import requests
import io
import tempfile
import wave
from pydub import AudioSegment
import yt_dlp
import re
import sys
from urllib.parse import urlparse, parse_qs


def baixar_para_memoria_ou_temp(url: str):
    if "youtube" in url or "yotu.be" in url:
        return baixar_youtube(url)
    elif "drive.google.com" in url:
        return baixar_drive(url)

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    s = requests.Session()
    resp = s.get(url, stream=True, timeout=30, headers=headers)
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
    arquivo = None
    temp_path = None

    try:
        if audios:
            tipo = "audio"
            if ext == ".wav" or ctype == "audio/wav":
                content.seek(0)
                arquivo = wave.open(content, "rb")
            else:
                fmt = ext.lstrip(".") if ext else None
                content.seek(0)
                if fmt:
                    arquivo = AudioSegment.from_file(content, format=fmt)
                else:
                    fd, temp_path = tempfile.mkstemp(suffix=ext)
                    os.close(fd)
                    with open(temp_path, "wb") as f:
                        f.write(content.getbuffer())
                    arquivo = AudioSegment.from_file(temp_path)
                    os.remove(temp_path)
                    temp_path = None
        elif fotos or videos:
            tipo = "imagem" if fotos else "videos"
            content.seek(0)
            arquivo = content
        else:
            tipo = "documento"
            content.seek(0)
            arquivo = content

        dados = {"arquivo": arquivo, "tipo": tipo, "nome": nome}
        return dados

    except Exception:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
        fd, temp_path = tempfile.mkstemp(suffix=ext)
        os.close(fd)
        with open(temp_path, "wb") as f:
            f.write(content.getbuffer())
        arquivo = open(temp_path, "rb")
        tipo = "documento"
        dados = {"arquivo": arquivo, "tipo": tipo,
                 "nome": nome, "_temp_path": temp_path}
        return dados


def baixar_youtube(url: str, prefer_audio=False, audio_format="mp3"):
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "outtmpl": os.path.join(tempfile.gettempdir(), "ydl_%(id)s.%(ext)s"),
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

    ext = os.path.splitext(filename)[1].lower()
    nome = os.path.basename(filename)

    if prefer_audio:
        audio = AudioSegment.from_file(filename, format=audio_format)
        try:
            os.remove(filename)
        except Exception:
            pass
        return {"arquivo": audio, "tipo": "audio", "nome": nome}
    else:
        f = open(filename, "rb")
        return {"arquivo": f, "tipo": "video", "nome": nome, "_temp_path": filename}


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
    chunk_size = 32768
    try:
        for chunk in response.iter_content(chunk_size):
            if chunk:
                content.write(chunk)
        content.seek(0)
        return {"arquivo": content, "tipo": tipo, "nome": nome}
    except Exception:
        fd, temp_path = tempfile.mkstemp(suffix=os.path.splitext(nome)[1])
        os.close(fd)
        with open(temp_path, "wb") as f:
            for chunk in response.iter_content(chunk_size):
                if chunk:
                    f.write(chunk)
        arquivo = open(temp_path, "rb")
        return {"arquivo": arquivo, "tipo": tipo, "nome": nome, "_temp_path": temp_path}
