import os
import requests
import io
import tempfile
import wave
from pydub import AudioSegment
import yt_dlp

import requests
import io
import os
import wave
import tempfile
from pydub import AudioSegment


def baixar_para_memoria_ou_temp(url: str):
    if "youtube" in url or "yotu.be" in url:
        baixar_youtube(url)

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
