from ttoken import Token
from simbolo import Simbolo

class TabelaSimbolos:
    def __init__ (self):
        # A pilha de escopos começa com o escopo global
        self.escopo = [{}]

    def entra_escopo (self):
        # Adiciona um novo dicionário vazio na pilha de escopos
        self.escopo.append({})

    def sai_escopo (self):
        # Remove o último escopo (nunca remove o global)
        if len(self.escopo) > 1: self.escopo.pop()

    def adicionar_simbolo (self, simbolo: Simbolo):
        escopo_atual = self.escopo[-1]
        # Verifica colisão de nomes no escopo atual
        if simbolo.nome in escopo_atual:
            return False, f"Identificador '{simbolo.nome}' já declarado neste escopo."
        escopo_atual[simbolo.nome] = simbolo
        return True, ""

    def procurar_simbolo (self, nome):
        # Busca do símbolo mais específico (topo) para o mais global (base)
        for escopo in reversed(self.escopo):
            if nome in escopo:
                return escopo[nome]
        return None

regras_operacoes_binarias = {
    # Soma
    frozenset({(Token.int_token, False), Token.mais, (Token.int_token, False)}): (Token.int_token, False),
    frozenset({(Token.float_token, False), Token.mais, (Token.float_token, False)}): (Token.float_token, False),
    frozenset({(Token.int_token, False), Token.mais, (Token.float_token, False)}): (Token.float_token, False),
    frozenset({(Token.char_token, False), Token.mais, (Token.char_token, False)}): (Token.int_token, False),
    frozenset({(Token.int_token, False), Token.mais, (Token.char_token, False)}): (Token.int_token, False),
    frozenset({(Token.float_token, False), Token.mais, (Token.char_token, False)}): (Token.float_token, False),

    # Substração
    frozenset({(Token.int_token, False), Token.menos, (Token.int_token, False)}): (Token.int_token, False),
    frozenset({(Token.float_token, False), Token.menos, (Token.float_token, False)}): (Token.float_token, False),
    frozenset({(Token.int_token, False), Token.menos, (Token.float_token, False)}): (Token.float_token, False),
    frozenset({(Token.char_token, False), Token.menos, (Token.char_token, False)}): (Token.int_token, False),
    frozenset({(Token.int_token, False), Token.menos, (Token.char_token, False)}): (Token.int_token, False),
    frozenset({(Token.float_token, False), Token.menos, (Token.char_token, False)}): (Token.float_token, False),

    # Multiplicação
    frozenset({(Token.int_token, False), Token.multiplicacao, (Token.int_token, False)}): (Token.int_token, False),
    frozenset({(Token.float_token, False), Token.multiplicacao, (Token.float_token, False)}): (Token.float_token, False),
    frozenset({(Token.int_token, False), Token.multiplicacao, (Token.float_token, False)}): (Token.float_token, False),
    frozenset({(Token.char_token, False), Token.multiplicacao, (Token.char_token, False)}): (Token.int_token, False),
    frozenset({(Token.int_token, False), Token.multiplicacao, (Token.char_token, False)}): (Token.int_token, False),
    frozenset({(Token.float_token, False), Token.multiplicacao, (Token.char_token, False)}): (Token.float_token, False),

    # Divisão
    frozenset({(Token.int_token, False), Token.divisao, (Token.int_token, False)}): (Token.int_token, False),
    frozenset({(Token.float_token, False), Token.divisao, (Token.float_token, False)}): (Token.float_token, False),
    frozenset({(Token.int_token, False), Token.divisao, (Token.float_token, False)}): (Token.float_token, False),
    frozenset({(Token.char_token, False), Token.divisao, (Token.char_token, False)}): (Token.int_token, False),
    frozenset({(Token.int_token, False), Token.divisao, (Token.char_token, False)}): (Token.int_token, False),
    frozenset({(Token.float_token, False), Token.divisao, (Token.char_token, False)}): (Token.float_token, False),

    # Módulo
    frozenset({(Token.int_token, False), Token.modulo, (Token.int_token, False)}): (Token.int_token, False),
    frozenset({(Token.char_token, False), Token.modulo, (Token.char_token, False)}): (Token.int_token, False),
    frozenset({(Token.int_token, False), Token.modulo, (Token.char_token, False)}): (Token.int_token, False),

    # Operações relacionais
    frozenset({(Token.int_token, False), Token.operador_relacional, (Token.int_token, False)}): (Token.int_token, False),
    frozenset({(Token.float_token, False), Token.operador_relacional, (Token.float_token, False)}): (Token.int_token, False),
    frozenset({(Token.char_token, False), Token.operador_relacional, (Token.char_token, False)}): (Token.int_token, False),
    frozenset({(Token.int_token, False), Token.operador_relacional, (Token.float_token, False)}): (Token.int_token, False),
    frozenset({(Token.int_token, False), Token.operador_relacional, (Token.char_token, False)}): (Token.int_token, False),
    frozenset({(Token.float_token, False), Token.operador_relacional, (Token.char_token, False)}): (Token.int_token, False),

    # Operações lógicas
    frozenset({(Token.int_token, False), Token.and_token, (Token.int_token, False)}): (Token.int_token, False),
    frozenset({(Token.int_token, False), Token.and_token, (Token.char_token, False)}): (Token.int_token, False),
    frozenset({(Token.char_token, False), Token.and_token, (Token.char_token, False)}): (Token.int_token, False),

    frozenset({(Token.int_token, False), Token.or_token, (Token.int_token, False)}): (Token.int_token, False),
    frozenset({(Token.int_token, False), Token.or_token, (Token.char_token, False)}): (Token.int_token, False),
    frozenset({(Token.char_token, False), Token.or_token, (Token.char_token, False)}): (Token.int_token, False),

    frozenset({(Token.char_token, True), Token.mais, (Token.char_token, True)}): (Token.char_token, True),
}

regras_operacoes_unarias = {
    (Token.menos, (Token.int_token, False)): (Token.int_token, False),
    (Token.menos, (Token.float_token, False)): (Token.float_token, False),
    (Token.menos, (Token.char_token, False)): (Token.int_token, False),

    (Token.mais, (Token.int_token, False)): (Token.int_token, False),
    (Token.mais, (Token.float_token, False)): (Token.float_token, False),
    (Token.mais, (Token.char_token, False)): (Token.int_token, False),

    (Token.not_token, (Token.int_token, False)): (Token.int_token, False),
    (Token.not_token, (Token.char_token, False)): (Token.int_token, False),
}

def checar_operacao_binaria (tipo_elemento_1, operacao, tipo_elemento_2):
    chave = frozenset({tipo_elemento_1, operacao, tipo_elemento_2})
    return regras_operacoes_binarias.get(chave, None)

def checar_operacao_unaria (operacao, tipo_elemento):
    chave = (operacao, tipo_elemento)
    return regras_operacoes_unarias.get(chave, None)

def checar_atribuicao (tipo_variavel, tipo_expressao):
    if tipo_variavel == tipo_expressao: return True

    # Não pode atribuir arrays diretamente (exceto string literal, tratada separadamente)
    if tipo_variavel[1]: return False
    if tipo_expressao[1]: return False
    if tipo_variavel == (Token.float_token, False) and tipo_expressao: return True
    if tipo_variavel == (Token.int_token, False) and tipo_expressao: return True
    if tipo_variavel[0] in {Token.int_token, Token.float_token, Token.char_token} and tipo_expressao[0] in {Token.int_token, Token.float_token, Token.char_token}: return True
    return False