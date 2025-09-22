class Usuario:
    def __init__(self):
        self.pixel_perfil = ""
        self.cor = ""
        self.status = ""
        self.nome = ""
        self.tempo = ""

    def get_pixel_perfil(self):
        return self.pixel_perfil

    def set_pixel_perfil(self, value):
        self.pixel_perfil = value

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
