from textual.screen import Screen
from textual.widgets import Input, TextArea, Static, ListItem, ListView, Button, Header, Footer
from textual.containers import HorizontalScroll, VerticalScroll, Container
from textual.events import Key
from textual.binding import Binding
from textual.timer import Timer
from database import Banco


class TelaInicial(Screen):
    CSS_PATH = "css/TelaInicial.tcss"
    nome_user = ""
    users = []
    mensagens = []
    _poll_timer: Timer = None

    BINDINGS = {
        Binding("ctrl+q", "sair", "Sair")
    }

    def action_sair(self):
        if self.nome_user:
            self.users = [
                u for u in self.users if not u.endswith(self.nome_user)]
            self.users.append(f"🔴 {self.nome_user}")
            Banco.salvar("banco.db", "usuarios", self.users)
            self.nome_user = ""
            self.app.exit()

    def compose(self):
        yield Header()
        with HorizontalScroll():
            with VerticalScroll():
                yield TextArea(disabled=True)  # read-only = True
                yield Input(placeholder="Digite aqui")
            yield ListView(id="lv_usuarios")
        yield Footer()

    def on_key(self, event: Key):
        if event.key == "enter" and self.nome_user:
            input_widget = self.query_one(Input)
            if input_widget.value:
                nova_mensagem = f"{self.nome_user}\n  {input_widget.value}\n"
                self.mensagens.append(nova_mensagem)
                Banco.salvar("banco.db", "mensagens", self.mensagens)
                self.query_one(TextArea).text += nova_mensagem
                input_widget.clear()

    def on_mount(self):
        carregar_users = Banco.carregar("banco.db", "usuarios")
        if carregar_users:
            self.users = carregar_users
        carregar_msgs = Banco.carregar("banco.db", "mensagens")
        if carregar_msgs:
            self.mensagens = carregar_msgs
            self.query_one(TextArea).text = "".join(self.mensagens)

        if not self.nome_user:
            for widget in self.screen.children:
                widget.disabled = True
            container = Container()
            self.mount(container)
            container.mount(Static("Ｌｏｇｉｎ", id="titulo"))
            container.mount(Static("Nome"))
            container.mount(Input(placeholder="Nome aqui", id="usuario"))
            container.mount(Button("Entrar"))

        self._poll_timer = self.set_interval(5, self.poll_dados)

    def poll_dados(self):
        carregar_users = Banco.carregar("banco.db", "usuarios")
        if carregar_users and carregar_users != self.users:
            self.users = carregar_users
            self.atualizar_lista_users()

        carregar_msgs = Banco.carregar("banco.db", "mensagens")
        if carregar_msgs and carregar_msgs != self.mensagens:
            self.mensagens = carregar_msgs
            self.query_one(TextArea).text = "".join(self.mensagens)

    def on_button_pressed(self):
        valor_input = self.query_one("#usuario", Input).value
        if valor_input:
            self.nome_user = valor_input
            if f"🟢 {self.nome_user}" not in self.users:
                self.users.append(f"🟢 {self.nome_user}")
            Banco.salvar("banco.db", "usuarios", self.users)
            self.query_one(Container).remove()
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
