from textual.app import App
from view import TelaInicial, TelaLogin, TelaServidor
from database import Banco
import io

class App(App):
    
    

    SCREENS = {
        "tela_login": TelaLogin.TelaLogin,
        "tela_inicial": TelaInicial.TelaInicial,
        "tela_servidor": TelaServidor.TelaServidor
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.usuario_logado = None  
    
    tela = "tela_login"
    servidor = False

    def on_mount(self):
            self.push_screen(self.tela)

    
    def action_pdf(self, hash):
        tela = self.get_screen("tela_inicial")
        try:
            tela.query_one(TelaInicial.ContainerDocumento).remove()
        except:
            container = TelaInicial.ContainerDocumento()
            tela.mount(container)
            blob = tela.documentos[hash]
            container.mount(TelaInicial.PDFViewer(path=io.BytesIO(blob)))