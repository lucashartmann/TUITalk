import asyncio
from textual_serve.server import Server
import sys
from aiohttp import web

comando = sys.argv[1:]

if "http" in comando or "https" in comando:

    servidor = Server(
        command="python Main.py",
        port=8000,
        host="0.0.0.0",
        public_url=comando[-1]
    )

else:
    servidor = Server(
        command="python Main.py",
        host=comando[-1],
        port=8000,
    )

servidor.serve()
