# tabela de simbolos[ident] -> tipo
# tabsimb['a']: [Token.int, false]
# se tivermos int vet[10], temos tabsimb['vet'] = [Token.int, true, 10]

# Para funções:
"""
char letra (int x, float y, int z[15])
tabsimb['letra'] = [
    [Token.function],
    [
        [Token.char, false], -> retorno
        [Token.int, false], -> primeiro parâmetro
        [Token.float, false], -> segundo parâmetro
        [Token.int, true, 15] -> terceiro parâmetro
    ]
]
"""

from ttoken import Token

class Semantico:
    def __init__(self, alvo):
        self.alvo = open(alvo, 'wt')
        self.escopos = [{}]

    def finaliza (self):
        self.alvo.close()

    # Adiciona um novo escopo à pilha
    def entra_escopo (self):
        self.escopos.append({})

    # Remove o último escopo da pilha
    def sai_escopo (self):
        self.escopos.pop()

    # Adiciona uma nova declaração no escopo
    def declara (self, nome, tipo):
        escopo_atual = self.escopos[-1]
        if nome in escopo_atual:
            print(f'Erro semântico: redeclaração de \"{nome}\" no escopo \"{escopo_atual}\"')
            raise Exception
        escopo_atual[nome] = tipo

    # Verifica se um nome foi declarado em algum escopo válido
    def verifica_declaracao (self, nome):
        for escopo in reversed(self.escopos):
            if nome in escopo:
                return escopo[nome]
        print(f'Erro semântico: \"{nome}\" no escopo \"{escopo}\" não foi declarado')
        raise Exception

    def verifica_tipo (self, tipo_esperado, tipo_real):
        if tipo_esperado != tipo_real:
            print(f'Erro semântico: tipo incompatível; esperava {tipo_esperado} e recebeu {tipo_real}')
            raise Exception

    def obter_tipo_token (self, identificador, linha, coluna):
        try:
            for escopo in self.escopos:
                if identificador in escopo:
                    return escopo[identificador]
            print(f'Variável \"{identificador}\" não declarada. Linha {linha}, coluna {coluna}')
            raise Exception
        except Exception as e:
            print(f'Erro inesperado: {e}')
            exit(1)

    def erro_semantico (self, token_atual, msg):
        (token, lexema, linha, coluna) = token_atual
        print(f'Erro na linha {linha}, coluna {coluna}: {msg}')
        raise Exception

    def gera (self, nivel, codigo):
        identacao = ' ' * 4 * nivel
        linha = identacao + codigo
        self.alvo.write(linha)