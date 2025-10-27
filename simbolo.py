class Simbolo:
    def __init__ (self, nome, tipo, categoria, array=False, params=None):
        self.nome = nome
        self.tipo = tipo
        self.categoria = categoria
        self.array = array
        self.params = params if params is not None else []