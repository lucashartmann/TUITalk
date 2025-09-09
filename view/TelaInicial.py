from textual.screen import Screen
from textual.widgets import Input, TextArea, Static, ListItem, ListView, Button
from textual.containers import HorizontalScroll, VerticalScroll
from textual.events import Key


class TelaInicial(Screen):

    CSS_PATH = "css/TelaInicial.tcss"

    def compose(self):
        with HorizontalScroll():
            with VerticalScroll():
                yield TextArea(disabled=True)
                yield Input(placeholder="Digite aqui")
            yield ListView(id="lv_usuarios")

    def _on_key(self, evento: Key):
        if evento.key == "enter":
            input = self.query_one(Input)
            if input.value:
                # LucasHartmann (colorido)
                    # Dia Lindo hoje!
                self.query_one(TextArea).text += input.value
                input.clear()
                
    # For usuario in usuarios logados:
    #   list_view.append(listitem(Static(🟢 LucasHartmann)))
    
    # if close program: self.atualizar_usuarios() ou 🔴 LucasHartmann
