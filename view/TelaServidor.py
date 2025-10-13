import os
import subprocess
import psutil
import requests
import asyncio

from ngrok import ngrok

from textual.screen import Screen
from textual.widgets import Switch, Static, Pretty, Input
from textual.binding import Binding

from database import Banco
import socket

class TelaServidor(Screen):
    

    BINDINGS = {
        Binding("q", "self.app.exit()", "Encerrar")
    }
    
    def compose(self):
        yield Input(placeholder="auth_token do ngrok")
        yield Static("Ligar Local:")
        yield Switch(value=False)
        yield Static("Ligar Ngrok")
        yield Switch(value=False, id="ngrok")
            
        yield Pretty("Servidor desligado")

    async def on_switch_changed(self, evento: Switch.Changed):
        if evento.switch.id == "ngrok":
            if evento.value == True:
                if self.query_one(Input).value != "":
                    token = self.query_one(Input).value
                    Banco.salvar("ngrok.db", "chave_ngrok", token)
                else:
                    token = Banco.carregar("ngrok.db", "chave_ngrok")

                try:
                    ngrok.set_auth_token(token)
                    self.listener = await ngrok.forward(8000, authtoken_from_env=False)

                except:
                    self.notify(f"ERRO! Insira seu token no Input")
                    return

                self.query_one(Pretty).update(self.listener.url())
                Banco.salvar("ngrok.db", "url", self.listener.url())
                os.environ["TEXTUAL_RUN"] = "1"
                self.proc = subprocess.Popen(
                    f'start cmd /k "cd {os.getcwd()} && python Serve.py {self.listener.url()}"',
                    shell=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
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
                os.environ["TEXTUAL_RUN"] = "0"
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
                        if "python serve.py" in cmd_str:
                            try:
                                p.terminate()
                            except Exception:
                                pass

                self.query_one(Pretty).update("Servidor desligado")
        else:
            if evento.value == True:
                host = self.get_local_ip()
                self.proc = subprocess.Popen(
                    f'start cmd /k "cd {os.getcwd()} && python Serve.py {host}"',
                    shell=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
                try:
                    cert_path = f"{os.getcwd()}/data/cert.pem"
                    key_path = f"{os.getcwd()}/data/key.pem"
                    print(key_path)
                    url = f"https://{host}:8000"
                except:
                    url = f"http://{host}:8000"
                Banco.salvar("ngrok.db", "url", url)
                self.query_one(Pretty).update(url)

            else:
                
                for p in psutil.process_iter(['pid', 'name', 'cmdline']):
                    cmd = p.info['cmdline']
                    if cmd:
                        cmd_str = ' '.join(cmd).lower()
                        if "python serve.py" in cmd_str:
                            try:
                                p.terminate()
                            except Exception:
                                pass
                self.query_one(Pretty).update("Servidor desligado")

    

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

    
