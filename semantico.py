# tabela de simbolos[ident] -> tipo
# tabsimb['a']: [Token.int, false]
# se tivermos int vet[10], temos tabsimb['vet'] = [Token.int, true, 10]

# Cada escopo possui uma tabela de simbolos

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

from tabela_simbolos import TabelaSimbolos, checar_atribuicao, checar_operacao_binaria, checar_operacao_unaria
from simbolo import Simbolo
from ttoken import Token

class Semantico:
    def __init__(self, alvo):
        # A tabela de símbolos gerencia escopos e variáveis
        self.tabela_simbolos = TabelaSimbolos()

        # Variáveis de controle de fluxo e verificação de tipos
        self.retorno_funcao_atual = None    # Tipo que a função retorna
        self.encontrou_retorno = False      # Verifica se há um 'return' na função
        self.nivel_laco = 0                 # Contador para saber se está dentro de um while/for para permitir break/continue

        # Inicializa as funções padrão
        self.declarar_funcoes_padrao()
        self.alvo = alvo

        # Abre o arquivo de saída no qual o código traduzido será escrito
        self.alvo = open(alvo, "wt", encoding='utf-8')

    def finaliza (self):
        self.alvo.close()

    def declarar_funcoes_padrao (self):
        # Registra funções nativas da linguagem na tabela de símbolos para que
        # qualquer parte do código possa chamá-las.

        putint = Simbolo(nome='putint', categoria='funcao', tipo=Token.int_token)
        putint.params.append({'tipo': Token.int_token, 'array': False})
        self.tabela_simbolos.adicionar_simbolo(putint)

        getint = Simbolo(nome='getint', categoria='funcao', tipo=Token.int_token)
        self.tabela_simbolos.adicionar_simbolo(getint)

        putfloat = Simbolo(nome='putfloat', categoria='funcao', tipo=Token.int_token)
        putfloat.params.append({'tipo': Token.float_token, 'array': False})
        self.tabela_simbolos.adicionar_simbolo(putfloat)

        getfloat = Simbolo(nome='getfloat', categoria='funcao', tipo=Token.float_token)
        self.tabela_simbolos.adicionar_simbolo(getfloat)

        putchar = Simbolo(nome='putchar', categoria='funcao', tipo=Token.int_token)
        putchar.params.append({'tipo': Token.char_token, 'array': False})
        self.tabela_simbolos.adicionar_simbolo(putchar)

        getchar = Simbolo(nome='getchar', categoria='funcao', tipo=Token.char_token)
        self.tabela_simbolos.adicionar_simbolo(getchar)

        putstr = Simbolo(nome='putstr', categoria='funcao', tipo=Token.int_token)
        putstr.params.append({'tipo': Token.char_token, 'array': True})
        self.tabela_simbolos.adicionar_simbolo(putstr)

    def entrar_escopo (self):
        self.tabela_simbolos.entra_escopo()

    def sair_escopo (self):
        self.tabela_simbolos.sai_escopo()

    def declarar_funcao (self, nome, retorno, token):
        # Cria o símbolo da função
        simbolo = Simbolo(nome=nome, categoria='funcao', tipo=retorno)
        sucesso, erro = self.tabela_simbolos.adicionar_simbolo(simbolo)
        if not sucesso:
            raise Exception(f'Erro semântico ao declarar função na linha {token[2]}: {erro}')

        # Prepara o contexto para analisar o corpo da função
        self.retorno_funcao_atual = retorno
        self.encontrou_retorno = False
        return simbolo

    def declarar_argumento (self, nome, tipo, array, lista_parametros, token):
        # Adiciona argumentos na lista de parâmetros da função no escopo local
        lista_parametros.append({'nome': nome, 'tipo': tipo, 'array': array})
        simbolo = Simbolo(nome=nome, categoria='variavel', tipo=tipo, array=array)
        sucesso, erro = self.tabela_simbolos.adicionar_simbolo(simbolo)
        if not sucesso:
            raise Exception(f'Erro semântico ao declarar argumento na linha {token[2]}: {erro}')

    def declarar_variavel (self, nome, tipo, array, token, tamanho=None):
        simbolo = Simbolo(nome=nome, categoria='variavel', tipo=tipo, array=array, tamanho=tamanho)
        sucesso, erro = self.tabela_simbolos.adicionar_simbolo(simbolo)
        if not sucesso:
            raise Exception(f'Erro semântico ao declarar variável na linha {token[2]}: {erro}')

    def verificar_identificador_declarado (self, nome, token):
        # Verifica se a variávle existe em algum escopo visível
        simbolo = self.tabela_simbolos.procurar_simbolo(nome)
        if simbolo is None:
            raise Exception(f'Erro semântico ao verificar identificador na linha {token[2]}: Identificador {nome} não declarado.')
        return simbolo

    def verificar_retorno (self, tipo, token):
        if self.retorno_funcao_atual is None:
            raise Exception(f'Erro semântico na linha {token[2]}: comando \'return\' encontrado fora de uma função')

        # Verifica se o tipo retornado é compatível com a assinatura da função
        tipo_esperado = (self.retorno_funcao_atual, False)
        if not checar_atribuicao(tipo_esperado, tipo):
            raise Exception(f'Erro semântico na linha {token[2]}: tipo de retorno incompatível. Esperava \'{Token.msg(self.retorno_funcao_atual)}\' mas recebey {tipo}.')

        self.encontrou_retorno = True

    def verificar_fluxo_retorno (self, token):
        # Garante que a função tem pelo menos um retorno
        if not self.encontrou_retorno:
            raise Exception(f'Erro semântico na linha {token[2]}: a função \'{token[1]}\' deve retonar um valor, mas nenhum \'return\' foi encontrado.')

    def entrar_laco (self):
        self.nivel_laco += 1

    def sair_laco (self):
        self.nivel_laco -= 1

    """ Verifica se os comandos break ou continue estão dentro de um laço. """
    def verificar_parada_laco (self, token):
        # Impede o uso de break ou continue fora de while/for
        if self.nivel_laco == 0:
            comando = Token.msg(token[0])
            raise Exception(f'Erro semântico na linha {token[2]}: Comando {comando} só pode ser usado dentro de um laço.')

    def validar_chamada_funcao (self, funcao: Simbolo, args, token):
        parametros_esperados = funcao.params

        # Verificando se o número de argumentos corresponde
        if len(args) != len(parametros_esperados):
            raise Exception(f'Erro semântico na linha {token[2]}: número incorreto de parâmetros para a função {funcao.nome}. Esperava {len(parametros_esperados)} mas recebeu {len(args)}.')

        # Verifica o tipo de cada argumento
        for i, tipo_argumento_passado in enumerate(args):
            parametro_esperado = parametros_esperados[i]
            tipo_esperado = (parametro_esperado['tipo'], parametro_esperado['array'])

            if not checar_atribuicao(tipo_esperado, tipo_argumento_passado):
                raise Exception(f'Erro semântico na linha {token[2]}: tipo incorreto para o {i + 1}º argumento da função {funcao.nome}. Esperava {tipo_esperado}, mas recebeu {tipo_argumento_passado}.')

    def validar_operacao_binaria (self, tipo_operador_esquerdo, operacao, tipo_operador_direito, token):
        # Consulta a matriz de operações
        tipo_resultado = checar_operacao_binaria(tipo_operador_esquerdo, operacao, tipo_operador_direito)
        if tipo_resultado is None:
            raise Exception(f'Erro semântico na linha {token[2]}: operação {Token.msg(operacao)} inválida para os tipos {tipo_operador_esquerdo} e {tipo_operador_direito}.')
        return tipo_resultado

    def validar_operacao_unaria (self, operacao, tipo_operando, token):
        tipo_resultado = checar_operacao_unaria(operacao, tipo_operando)
        if tipo_resultado is None:
            raise Exception(f'Erro semântico na linha {token[2]}: operador unário {Token.msg(operacao)} inválido para o tipo {tipo_operando}.')
        return tipo_resultado

    def validar_atribuicao (self, tipo_variavel, tipo_expressao, token):
        # Verifica se pode atribuir valor à variável
        if not checar_atribuicao(tipo_variavel, tipo_expressao):
            raise Exception(f'Erro semântico na linha {token[2]}: atribuição incompatível. Impossível atribuir {tipo_expressao} a {tipo_variavel}.')

    def gera (self, nivel, codigo):
        # Escreve o código Python no arquivo de saída
        # O nível controla a indentação
        identacao = ' ' * 4 * nivel
        linha = identacao + codigo
        self.alvo.write(linha)