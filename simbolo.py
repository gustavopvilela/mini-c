class Simbolo:
    def __init__ (self, nome, tipo, categoria, array=False, tamanho=None, params=None):
        self.nome = nome
        self.tipo = tipo
        self.categoria = categoria
        self.array = array # True: variável é array; False caso contrário
        self.tamanho = tamanho # Tamanho da variável se for array
        self.params = params if params is not None else []