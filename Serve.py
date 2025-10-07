import asyncio
from textual_serve.server import Server
import sys
from aiohttp import web

comando = sys.argv[1:]

servidor = Server(
    command="python Main.py",
    port=8000,
    host="0.0.0.0",
    public_url=comando[-1] 
)

async def escutar_comandos(server):
    while True:
        print("escutar_comandos() chamado")
        cmd = sys.stdin.readline().strip()
        if hasattr(server, "ws_js") and server.ws_js is not None:
            print("server.ws_js tudo certo")
            await server.ws_js.send_str(cmd)  # envia para o JS
        print("server.ws_js nao esta certo")
        await asyncio.sleep(0.01)  # ev


servidor.serve() 

