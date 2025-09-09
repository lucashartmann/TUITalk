from textual.screen import Screen
from textual.widgets import Input, TextArea, Static, ListItem, ListView, Button
from textual.containers import HorizontalGroup, VerticalGroup
from textual.events import Key


class TelaInicial(Screen):

    CSS_PATH = "css/TelaInicial.tcss"

    def compose(self):
        with HorizontalGroup():
            with VerticalGroup():
                yield TextArea(read_only=True)
                yield Input(placeholder="Digite aqui")
            yield ListView(id="lv_usuarios")

    def _on_key(self, evento: Key):
        if evento.key == "enter":
            input = self.query_one(Input)
            if input.value:
                self.query_one(TextArea).text += input.value
                input.clear()
