from ttoken import Token
from estados import Estado

class Lexico:
    def __init__(self, arquivo):
        self.arquivo = arquivo                          # Arquivo do código .toy
        self.codigo_fonte = self.arquivo.read()         # String do código
        self.tamanho_codigo = len(self.codigo_fonte)    # Tamanho do código
        self.indice = 0                                 # Onde se está no arquivo
        self.linha = 1                                  # Linha atual
        self.coluna = 0                                 # Coluna atual

    def fim_de_arquivo (self):
        return self.indice >= self.tamanho_codigo

    def descartar_brancos_e_comentarios (self):
        while not self.fim_de_arquivo():
            caractere = self.get_char()

            if caractere == ' ' or caractere == '\n' or caractere == '\t':   # O caractere é um espaço, quebra de linha ou tabulação
                continue
            elif caractere == '/':  # Ler comentário
                proximo_caractere = self.get_char()
                if proximo_caractere == '/':
                    while not self.fim_de_arquivo():
                        caractere_comentario = self.get_char()
                        if caractere_comentario == '\n' or caractere_comentario == '\0':
                            break
                else:
                    self.unget_char()
                    self.unget_char()
                    break
            else:   # O caractere não se enquadra nas condições anteriores
                self.unget_char()
                break

    def get_char(self):
        if self.indice >= self.tamanho_codigo:
            return '\0'

        caractere = self.codigo_fonte[self.indice]
        self.indice += 1

        if caractere == '\n':
            self.linha += 1
            self.coluna = 0
        else:
            self.coluna += 1

        return caractere

    def unget_char(self):
        if self.indice == 0:
            return

        self.indice -= 1
        caractere_devolvido = self.codigo_fonte[self.indice]

        if caractere_devolvido == '\n':
            self.linha -= 1
        else:
            self.coluna -= 1

    def imprimir_token (self, id, lexema, linha, coluna):
        print(f'Linha: {linha}, Coluna: {coluna} -> <{id}, "{lexema}">')

    def get_token (self):
        self.descartar_brancos_e_comentarios()

        estado = Estado.INICIAL
        lexema = ""

        while True:
            simbolo = self.get_char()

            # print(f"SÍMBOLO: {simbolo} | LEXEMA: {lexema}")

            if estado == Estado.INICIAL:
                if simbolo.isalpha() or simbolo == '_':
                    estado = Estado.IDENTIFICADOR
                    lexema += simbolo
                elif simbolo.isdigit():
                    estado = Estado.VALOR_INT
                    lexema += simbolo
                elif simbolo == '>':
                    estado = Estado.OP_REL_MAIOR
                    lexema += simbolo
                elif simbolo == '<':
                    estado = Estado.OP_REL_MENOR
                    lexema += simbolo
                elif simbolo == '=':
                    estado = Estado.OP_REL_IGUAL
                    lexema += simbolo
                elif simbolo == '!':
                    estado = Estado.OP_REL_DIFERENTE
                    lexema += simbolo
                elif simbolo == '&':
                    estado = Estado.AND
                    lexema += simbolo
                elif simbolo == '|':
                    estado = Estado.OR
                    lexema += simbolo
                elif simbolo == '"': estado = Estado.VALOR_STRING
                elif simbolo == "'": estado = Estado.VALOR_CHAR
                elif simbolo == '+': return Token.mais, Token.msg(Token.mais), self.linha, self.coluna
                elif simbolo == '-': return Token.menos, Token.msg(Token.menos), self.linha, self.coluna
                elif simbolo == '*': return Token.multiplicacao, Token.msg(Token.multiplicacao), self.linha, self.coluna
                elif simbolo == '/': return Token.divisao, Token.msg(Token.divisao), self.linha, self.coluna
                elif simbolo == '%': return Token.modulo, Token.msg(Token.modulo), self.linha, self.coluna
                elif simbolo == '(': return Token.abre_parentese, Token.msg(Token.abre_parentese), self.linha, self.coluna
                elif simbolo == ')': return Token.fecha_parentese, Token.msg(Token.fecha_parentese), self.linha, self.coluna
                elif simbolo == '[': return Token.abre_colchete, Token.msg(Token.abre_colchete), self.linha, self.coluna
                elif simbolo == ']': return Token.fecha_colchete, Token.msg(Token.fecha_colchete), self.linha, self.coluna
                elif simbolo == '{': return Token.abre_chave, Token.msg(Token.abre_chave), self.linha, self.coluna
                elif simbolo == '}': return Token.fecha_chave, Token.msg(Token.fecha_chave), self.linha, self.coluna
                elif simbolo == ',': return Token.virgula, Token.msg(Token.virgula), self.linha, self.coluna
                elif simbolo == ';': return Token.ponto_virgula, Token.msg(Token.ponto_virgula), self.linha, self.coluna
                elif simbolo == '\0': return Token.eof, Token.msg(Token.eof), self.linha, self.coluna
                else: return Token.erro, simbolo, self.linha, self.coluna

            elif estado == Estado.IDENTIFICADOR:
                if simbolo.isalnum() or simbolo == '_':
                    lexema += simbolo
                elif simbolo == '(':
                    self.unget_char()
                    if Token.reservadas(lexema) == Token.identificador:
                        return Token.funcao, lexema, self.linha, self.coluna
                    else:
                        return Token.reservadas(lexema), lexema, self.linha, self.coluna
                else:
                    self.unget_char()
                    return Token.reservadas(lexema), lexema, self.linha, self.coluna

            elif estado == Estado.VALOR_INT:
                if simbolo.isdigit():
                    lexema += simbolo
                elif simbolo == '.':
                    estado = Estado.VALOR_FLOAT
                    lexema += simbolo
                else:
                    self.unget_char()
                    return Token.valor_int, lexema, self.linha, self.coluna

            elif estado == Estado.VALOR_FLOAT:
                if simbolo.isdigit():
                    lexema += simbolo
                else:
                    self.unget_char()
                    return Token.valor_float, lexema, self.linha, self.coluna

            elif estado == Estado.VALOR_STRING:
                if simbolo == '"':
                    return Token.valor_string, lexema, self.linha, self.coluna
                elif simbolo == '\0':
                    return Token.erro, lexema, self.linha, self.coluna
                else:
                    lexema += simbolo

            elif estado == Estado.VALOR_CHAR:
                if simbolo == "'":
                    return Token.valor_char, lexema, self.linha, self.coluna
                elif simbolo == '\0':
                    return Token.erro, lexema, self.linha, self.coluna
                else:
                    lexema += simbolo

            elif estado in [Estado.OP_REL_MAIOR, Estado.OP_REL_MENOR, Estado.OP_REL_IGUAL, Estado.OP_REL_DIFERENTE]:
                if simbolo == '=':
                    lexema += simbolo
                    return Token.operador_relacional, lexema, self.linha, self.coluna

                else:
                    self.unget_char()
                    if estado == Estado.OP_REL_IGUAL:
                        return Token.atribuicao, lexema, self.linha, self.coluna
                    elif estado == Estado.OP_REL_DIFERENTE:
                        return Token.not_token, lexema, self.linha, self.coluna
                    else:
                        return Token.operador_relacional, lexema, self.linha, self.coluna

            elif estado == Estado.AND:
                if simbolo == '&':
                    lexema += simbolo
                    return Token.and_token, lexema, self.linha, self.coluna
                else:
                    self.unget_char()
                    return Token.erro, lexema, self.linha, self.coluna

            elif estado == Estado.OR:
                if simbolo == '|':
                    lexema += simbolo
                    return Token.or_token, lexema, self.linha, self.coluna
                else:
                    self.unget_char()
                    return Token.erro, lexema, self.linha, self.coluna