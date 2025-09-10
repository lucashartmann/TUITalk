from textual.screen import Screen
from textual.widgets import Input, TextArea, Static, ListItem, ListView, Button, Header, Footer
from textual.containers import HorizontalScroll, VerticalScroll, Container
from textual.events import Key
from textual.binding import Binding
from textual.message import Message
from database import Banco


class ChatMessage(Message):
    def __init__(self, sender, text):
        super().__init__()
        self.sender = sender
        self.text = text


class UpdateUsers(Message):
    def __init__(self, users):
        super().__init__()
        self.users = users


class TelaInicial(Screen):

    CSS_PATH = "css/TelaInicial.tcss"
    nome_user = ""
    users = list()

    BINDINGS = {
        Binding("ctrl+q", "d", "Sair")
    }

    def action_sair(self):
        for user in self.users:
            if self.nome_user == user:
                user = f"🔴{self.nome_user}"
        self.screen.app.exit()

    def compose(self):
        yield Header()
        with HorizontalScroll():
            with VerticalScroll():
                yield TextArea(disabled=True)  # read-only = True
                yield Input(placeholder="Digite aqui")
            yield ListView(id="lv_usuarios")
        yield Footer()

    def on_key(self, event: Key):
        if event.key == "enter":
            input_widget = self.query_one(Input)
            if input_widget.value:
                message = ChatMessage(self.nome_user, input_widget.value)
                self.post_message(message)
                input_widget.clear()

    def on_mount(self):
        carregar = Banco.carregar("banco.db", "usuarios")
        if carregar:
            self.users = carregar
        if not self.nome_user:
            for widget in self.screen.children:
                widget.disabled = True
            container = Container()
            self.mount(container)
            container.mount(Static("Ｌｏｇｉｎ", id="titulo"))
            container.mount(Static("Nome"))
            container.mount(Input(placeholder="Nome aqui", id="usuario"))
            container.mount(Button("Entrar"))

    def on_button_pressed(self):
        valor_input = self.query_one("#usuario", Input).value
        if valor_input:
            self.nome_user = self.query_one("#usuario", Input).value
            self.users.append(f"🟢 {self.nome_user}")
            self.query_one(Container).remove()
            self.post_message(UpdateUsers(self.users))
            for widget in self.screen.children:
                widget.disabled = False
            self.atualizar_lista_users()
        else:
            self.notify("Valor inválido")

    def atualizar_lista_users(self):
        lista = self.query_one("#lv_usuarios", ListView)
        lista.remove_children()

        for user in self.users:
            lista.append(ListItem(Static(user)))

    def on_chat_message(self, message: ChatMessage):
        self.query_one(
            TextArea).text += f"{message.sender}\n  {message.text}\n"

    def on_update_users(self):
        Banco.salvar("banco.db", "usuarios", self.users)
        carregar = Banco.carregar("banco.db", "usuarios")
        if carregar:
            self.users = carregar
        self.atualizar_lista_users()
