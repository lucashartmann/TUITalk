import os
import subprocess
import psutil
import requests
import time

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
            self.query_one(
                Input).value = "32WRv5r1RrayKRcgjGzLvOoDEcU_4GJkbq7eovEWX1Zpzt2DU"
            ngrok.set_auth_token(
                "32WRv5r1RrayKRcgjGzLvOoDEcU_4GJkbq7eovEWX1Zpzt2DU")
            # Banco.salvar("banco.db", "chave_ngrok", token)

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

            time.sleep(1)
            self.notify(f"Enviando URL para Vercel: {self.listener.url()}")
            try:
                storage_url = "https://textual-message.vercel.app/api/storage"
                self.notify(f"POST para: {storage_url}")
                response = requests.post(
                    storage_url,
                    json={"url": self.listener.url()},
                    timeout=10
                )
                self.notify(
                    f"Resposta Storage: {response.status_code} - {response.text}")

                if response.status_code == 200:
                    self.notify("URL enviada com sucesso para o Storage!")
                else:
                    self.notify("Tentando endpoint original...")
                    fallback_url = "https://textual-message.vercel.app/api/set-url"
                    fallback_response = requests.post(
                        fallback_url,
                        json={"url": self.listener.url()},
                        timeout=10
                    )
                    self.notify(
                        f"Resposta Fallback: {fallback_response.status_code} - {fallback_response.text}")
                    if fallback_response.status_code == 200:
                        self.notify("URL enviada com sucesso (fallback)!")
                    else:
                        self.notify(
                            f"Erro ao enviar URL: {fallback_response.status_code}")
            except requests.exceptions.RequestException as e:
                self.notify(f"Erro de conexão: {e}")

        else:
            if self.listener:
                self.listener.close()

            try:
                self.notify("Limpando URL do storage...")
                storage_url = "https://textual-message.vercel.app/api/storage"
                response = requests.delete(storage_url, timeout=10)
                if response.status_code == 200:
                    self.notify("URL removida do storage!")
                else:
                    self.notify(
                        f"Erro ao limpar storage: {response.status_code}")
            except requests.exceptions.RequestException as e:
                self.notify(f"Erro ao conectar com storage: {e}")

            for p in psutil.process_iter(['pid', 'name', 'cmdline']):
                cmd = p.info['cmdline']
                if cmd:
                    cmd_str = ' '.join(cmd).lower()
                    if 'textual' in cmd_str or 'cmd.exe' in cmd_str or 'python' in cmd_str:
                        try:
                            p.terminate()
                        except Exception:
                            pass

            self.query_one(Pretty).update("Servidor desligado")
