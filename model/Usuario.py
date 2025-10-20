class Usuario:
    def __init__(self):
        self.id = ""
        self.foto = ""
        self.cor = ""
        self.status = ""
        self.nome = ""
        self.tempo = ""

    def get_id(self):
        return self.id

    def set_id(self, novo_id):
        self.id = novo_id

    def get_foto(self):
        return self.foto

    def set_foto(self, nova_foto):
        self.foto = nova_foto

    def get_cor(self):
        return self.cor

    def set_cor(self, value):
        self.cor = value

    def get_status(self):
        return self.status

    def set_status(self, value):
        self.status = value

    def get_nome(self):
        return self.nome

    def set_nome(self, value):
        self.nome = value

    def get_tempo(self):
        return self.tempo

    def set_tempo(self, value):
        self.tempo = value
