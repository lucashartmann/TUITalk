import os
import subprocess
import psutil
import requests
import asyncio

from ngrok import ngrok

from textual.screen import Screen
from textual.widgets import Switch, Static, Pretty, Input

from database import Banco


class TelaServidor(Screen):

    listener = ""

    def compose(self):
        yield Input(placeholder="auth_token do ngrok")
        yield Static("Ligar Servidor:")
        yield Switch(value=False)
        yield Pretty("Servidor desligado")

    async def on_switch_changed(self, evento: Switch.Changed):
        if evento.value == True:
            if self.query_one(Input).value != "":
                token = str(self.query_one(Input).value)
                Banco.salvar("banco.db", "chave_ngrok", token)
            else:
                token = str(Banco.carregar("banco.db", "chave_ngrok"))
                if not token:
                    if self.query_one(Input).value == "":
                        self.notify("ERRO! Chave do ngrok em branco")
                        return
                    else:
                        token = str(self.query_one(Input).value)
                        Banco.salvar("banco.db", "chave_ngrok", token)

            try:
                ngrok.set_auth_token(token)
            except:
                self.notify("ERRO! ngrok.set_auth_token()")
                return

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

            await asyncio.sleep(1)
            try:
                storage_url = "https://textual-message.vercel.app/api/storage"
                response = requests.post(
                    storage_url,
                    json={"url": self.listener.url()},
                    timeout=10
                )

                if not response.status_code == 200:

                    fallback_url = "https://textual-message.vercel.app/api/set-url"
                    fallback_response = requests.post(
                        fallback_url,
                        json={"url": self.listener.url()},
                        timeout=10
                    )

                    if not fallback_response.status_code == 200:
                        self.notify(
                            f"Erro ao enviar URL: {fallback_response.status_code}")
            except requests.exceptions.RequestException as e:
                self.notify(f"Erro de conexão: {e}")

        else:
            if self.listener:
                self.listener.close()

            try:
                storage_url = "https://textual-message.vercel.app/api/storage"
                response = requests.delete(storage_url, timeout=10)
                if not response.status_code == 200:

                    self.notify(
                        f"Erro ao limpar storage: {response.status_code}")
            except requests.exceptions.RequestException as e:
                self.notify(f"Erro ao conectar com storage: {e}")

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
