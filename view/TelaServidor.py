import os
import subprocess
import psutil
import requests

from ngrok import ngrok

from textual.screen import Screen
from textual.screen import Screen
from textual.widgets import Switch, Static, Pretty, Input

from database import Banco

from api import index


class TelaServidor(Screen):

    listener = ""

    def compose(self):
        yield Input(placeholder="auth_token do ngrok")
        yield Static("Ligar Servidor:")
        yield Switch(value=False)
        yield Pretty("Servidor desligado")

    async def on_switch_changed(self, evento: Switch.Changed):
        if evento.value == True:
                token = self.query_one(Input).value
                ngrok.set_auth_token(token)
                Banco.salvar("banco.db", "chave_ngrok", token)

                self.listener = await ngrok.forward(8000, authtoken_from_env=False)
                self.query_one(Pretty).update(self.listener.url())
                os.environ["TEXTUAL_RUN"] = "1"
                self.proc = subprocess.Popen(
                    [
                        "start", "cmd", "/k",
                        f"textual serve Main.py --port 8000 --host 0.0.0.0 --url {self.listener.url()}"
                    ],
                    shell=True
                )

                requests.post(
                    "https://textual-message.vercel.app",
                    json={"url": self.listener.url()}
                )

            
        else:
            self.listener.close()
            for p in psutil.process_iter(['pid', 'name', 'cmdline']):
                cmd = p.info['cmdline']
                if cmd:
                    cmd_str = ' '.join(cmd).lower()
                    if 'textual' in cmd_str or 'cmd.exe' in cmd_str:
                        try:
                            p.terminate()
                        except Exception:
                            pass
            self.query_one(Pretty).update("Servidor desligado")
