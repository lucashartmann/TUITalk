from textual.containers import Container
from textual.widgets import Static, Input, ListView, ListItem
from textual.events import Click
from textual.message import Message
import os
import wave
from pydub import AudioSegment



class TelaSelecionar(Container):
    
    class Selecionado(Message):
            def __init__(self, valor: dict):
                super().__init__()
                self.sender = TelaSelecionar
                self.valor = valor

    caminho = "C:\\Users\\dudua\\OneDrive\\Imagens"

    lista_arquivos = os.listdir(caminho)

    extensoes_fotos = [
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp", ".heif", ".heic",
        ".raw", ".cr2", ".nef", ".orf", ".sr2", ".arw", ".dng", ".ico", ".svg", ".psd", ".xcf"
    ]

    extensoes_videos = [
        ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mpg", ".mpeg", ".3gp",
        ".ogv", ".m4v", ".f4v", ".ts", ".vob", ".rm", ".rmvb"
    ]

    extensoes_documentos = [
        ".pdf", ".doc", ".docx", ".odt", ".rtf", ".txt", ".md", ".tex",
        ".ppt", ".pptx", ".odp", ".pps", ".key",
        ".xls", ".xlsx", ".ods", ".csv", ".tsv",
        ".epub", ".mobi", ".azw3", ".chm"
    ]

    extensoes_audios = [
        ".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".opus", ".alac", ".aiff", ".amr", ".au", ".ra", ".mid", ".midi"
    ]

    def compose(self):
        yield Input("")
        yield ListView(id="lst_item")

        id = "janela"
        
    def on_mount(self):
        self.query_one(Input).value = "C:\\Users\\dudua\\OneDrive\\Imagens"
        self.atualizar_lista_arquivos()

    def on_click(self, evento: Click):
        if evento.widget.parent.parent.id == "lst_item" and evento.chain == 2:
            if isinstance(evento.widget, Static):
                static_clicado = evento.widget.content
                try:
                    arquivo = open(f"{self.caminho}\\{static_clicado}", "rb")
                    tipo = ""
                    if static_clicado[static_clicado.index("."):] in self.extensoes_fotos:
                        tipo = "imagem"
                    elif static_clicado[static_clicado.index("."):] in self.extensoes_videos:
                        tipo = "video"
                    elif static_clicado[static_clicado.index("."):] in self.extensoes_audios:
                        if static_clicado[static_clicado.index("."):] == ".wav":
                            arquivo = wave.open(f"{self.caminho}\\{static_clicado}", "rb")
                        else:
                            arquivo = AudioSegment.from_file(f"{self.caminho}\\{static_clicado}")

                        tipo = "audio"
                    else:
                        tipo = "documento"
                    dados = {"arquivo": arquivo,
                             "tipo": tipo, "nome": static_clicado}
                    self.post_message(self.Selecionado(dados))
                    self.remove()
                except Exception as e:
                    self.notify(f"ERRO! {e}")
                    return

    def on_input_changed(self, evento: Input.Changed):
        try:
            self.caminho = evento.input.value
            self.lista_arquivos = os.listdir(self.caminho)
        except:
            self.notify(f"ERRO! Caminho {evento.input.value}")
            return

        self.atualizar_lista_arquivos()

    def atualizar_lista_arquivos(self):
        list_view = self.query_one(ListView)
        list_view.clear()

        for arquivo in self.lista_arquivos:
            try:
                if arquivo[arquivo.index("."):] in self.extensoes_fotos or arquivo[arquivo.index("."):] in self.extensoes_videos or arquivo[arquivo.index("."):] in self.extensoes_documentos or arquivo[arquivo.index("."):] in self.extensoes_audios:
                    list_view.append(ListItem(Static(arquivo)))
            except:
                pass


