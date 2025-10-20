class Simbolo:
    def __init__ (self, nome, tipo, array=False, params=None):
        self.nome = nome
        self.tipo = tipo
        self.array = array
        self.params = params if params is not None else []