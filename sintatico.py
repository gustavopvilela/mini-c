from simbolo import Simbolo
from ttoken import Token
from lexico import Lexico
from semantico import Semantico

class Sintatico:
    def __init__(self, lexico: Lexico, alvo: str = "saida.py"):
        self.lexico = lexico
        self.token_lido = None
        self.semantico = Semantico(alvo)

    def traduz(self):
        self.token_lido = self.lexico.get_token()
        try:
            self.semantico.gera(0, 'def putint(x): print(x, end="", flush=True)\n')
            self.semantico.gera(0, 'def putfloat(x): print(float(x), end="", flush=True)\n')
            self.semantico.gera(0, 'def putstr(x): print(x, end="", flush=True)\n')
            self.semantico.gera(0, 'def putchar(x): print(chr(x) if isinstance(x, int) else x, end="", flush=True)\n')
            self.semantico.gera(0, 'def getint(): return int(input())\n')
            self.semantico.gera(0, 'def getfloat(): return float(input())\n')
            self.semantico.gera(0, 'def getchar(): return input()[0]\n\n')

            self.semantico.gera(0, 'class Programa:\n')
            self.semantico.gera(1, 'def __init__(self):\n')
            self.semantico.gera(2, 'pass\n\n')

            self.Program()
            self.consome(Token.eof)
            print("Traduzido com sucesso!")
            return True
        except Exception as e:
            print(f"Ocorreu um erro durante a tradução. {e}")
            return False

    def consome(self, token_atual):
        (token, lexema, linha, coluna) = self.token_lido
        if token_atual == token:
            self.token_lido = self.lexico.get_token()
        else:
            msg_token_lido = Token.msg(token)
            msg_token_atual = Token.msg(token_atual)

            print(f'Erro na linha {linha}, coluna {coluna}: ', end="")

            if token == Token.erro:
                msg = lexema
            else:
                msg = msg_token_lido

            print(f'esperava \"{msg_token_atual}\" mas recebeu \"{msg}\".')

            raise Exception

    def testa_lexico(self):
        self.token_lido = self.lexico.get_token()
        (token, lexema, linha, coluna) = self.token_lido

        while token != Token.eof:
            self.lexico.imprimir_token(token, lexema, linha, coluna)
            self.token_lido = self.lexico.get_token()
            (token, lexema, linha, coluna) = self.token_lido

    # Program -> Function Program | LAMBDA
    def Program (self):
        if self.token_lido[0] in [Token.int_token, Token.float_token, Token.char_token]:
            self.Function()
            self.Program()
        elif self.token_lido[0] == Token.eof:
            self.semantico.gera(0, '\nif __name__ == \'__main__\':\n')
            self.semantico.gera(1, 'programa = Programa()\n')
            self.semantico.gera(1, 'programa.main()\n')
        else:
            print(f"Erro Sintático: Início de programa inesperado com o token '{self.token_lido[1]}' na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    # Function -> Type ident ( ArgList ) CompoundStmt
    def Function (self):
        # Capturando o tipo de retorno
        tipo_retorno = self.Type()
        nome_funcao = self.token_lido[1]
        token_funcao = self.token_lido

        self.consome(Token.identificador)

        # Declarando a função no semântico
        simbolo_funcao = self.semantico.declarar_funcao(nome=nome_funcao, retorno=tipo_retorno, token=token_funcao)

        self.consome(Token.abre_parentese)

        # Entrando em um novo escopo
        self.semantico.entrar_escopo()

        # Passando a lista de parâmetros da função para a função ArgList
        self.ArgList(simbolo_funcao.params)

        self.consome(Token.fecha_parentese)

        if simbolo_funcao.params:
            parametros = ', '.join([param['nome'] for param in simbolo_funcao.params])
            self.semantico.gera(1, f'def {nome_funcao}(self, {parametros}):\n')
        else:
            self.semantico.gera(1, f'def {nome_funcao}(self):\n')

        self.CompoundStmt(2)

        # Sai do escopo
        self.semantico.sair_escopo()
        self.semantico.gera(0, '\n')

    # ArgList -> Arg RestoArgList | LAMBDA
    def ArgList (self, lista_parametros):
        if self.token_lido[0] in [Token.int_token, Token.float_token, Token.char_token]:
            self.Arg(lista_parametros)
            self.RestoArgList(lista_parametros)
        elif self.token_lido[0] == Token.fecha_parentese:
            pass
        else:
            print(f"Erro Sintático: Lista de argumentos inválida na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    # RestoArgList -> , Arg RestoArgList | LAMBDA
    def RestoArgList (self, lista_parametros):
        if self.token_lido[0] == Token.virgula:
            self.consome(Token.virgula)
            self.Arg(lista_parametros)
            self.RestoArgList(lista_parametros)
        elif self.token_lido[0] == Token.fecha_parentese:
            pass
        else:
            print(f"Erro Sintático: Argumento adicional mal formado na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    # Arg -> Type IdentArg
    def Arg (self, lista_parametros):
        tipo_argumento = self.Type()
        nome_argumento, array = self.IdentArg()

        # Declarando o argumento da função
        self.semantico.declarar_argumento(nome=nome_argumento, tipo=tipo_argumento, array=array, lista_parametros=lista_parametros, token=self.token_lido)

    # IdentArg -> ident OpcIdentArg
    def IdentArg (self):
        nome_argumento = self.token_lido[1]
        self.consome(Token.identificador)
        array = self.OpcIdentArg() # Verifica se o argumento é um vetor ou não
        return nome_argumento, array

    # OpcIdentArg -> [ ] | LAMBDA
    def OpcIdentArg (self):
        if self.token_lido[0] == Token.abre_colchete:
            self.consome(Token.abre_colchete)
            self.consome(Token.fecha_colchete)
            return True # O argumento é um vetor
        elif self.token_lido[0] in [Token.virgula, Token.fecha_parentese]:
            return False # O argumento não é um vetor
        else:
            print(f"Erro Sintático: Argumento de array mal formado na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    # CompoundStmt -> { StmtList }
    def CompoundStmt(self, indentacao = 1):
        self.consome(Token.abre_chave)

        # Entrando em um novo escopo
        self.semantico.entrar_escopo()

        self.StmtList(indentacao)
        self.consome(Token.fecha_chave)

        # Saindo do escopo
        self.semantico.sair_escopo()

    # StmtList -> Stmt StmtList | LAMBDA
    def StmtList(self, indentacao = 1):
        # Conjunto First para a variável StmtList
        comandos_possiveis = [
            Token.for_token, Token.while_token, Token.if_token, Token.abre_chave,
            Token.break_token, Token.continue_token, Token.return_token, Token.ponto_virgula,
            Token.int_token, Token.float_token, Token.char_token, Token.identificador,
            Token.valor_int, Token.valor_float, Token.valor_char, Token.valor_string,
            Token.abre_parentese, Token.mais, Token.menos, Token.not_token
        ]

        if self.token_lido[0] in comandos_possiveis:
            self.Stmt(indentacao)
            self.StmtList(indentacao)
        elif self.token_lido[0] == Token.fecha_chave:
            pass
        else:
            print(f"Erro Sintático: Declaração ou expressão inválida na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    def Stmt (self, indentacao = 1):
        # Conjunto First da variável Stmt
        comandos_possiveis = {
            Token.identificador, Token.valor_int, Token.valor_float,
            Token.valor_char, Token.valor_string, Token.abre_parentese,
            Token.mais, Token.menos, Token.not_token
        }

        token = self.token_lido
        tipo_token = token[0]

        if tipo_token == Token.for_token:
            self.semantico.entrar_laco()
            self.ForStmt(indentacao)
            self.semantico.sair_laco()

        elif tipo_token == Token.while_token:
            self.semantico.entrar_laco()
            self.WhileStmt(indentacao)
            self.semantico.sair_laco()

        elif tipo_token == Token.if_token:
            self.IfStmt(indentacao)

        elif tipo_token == Token.abre_chave:
            self.CompoundStmt(indentacao)

        elif tipo_token in {Token.int_token, Token.float_token, Token.char_token}:
            self.Declaration(indentacao)

        elif tipo_token == Token.break_token:
            self.semantico.verificar_parada_laco(token)
            self.consome(Token.break_token)
            self.consome(Token.ponto_virgula)
            self.semantico.gera(indentacao, 'break\n')

        elif tipo_token == Token.continue_token:
            self.semantico.verificar_parada_laco(token)
            self.consome(Token.continue_token)
            self.consome(Token.ponto_virgula)
            self.semantico.gera(indentacao, 'continue\n')

        elif tipo_token == Token.return_token:
            self.consome(Token.return_token)

            # Pegando o retorno da expressão
            tipo_expressao, codigo_expressao, _ = self.Expr()

            # Verificando o tipo de retorno
            self.semantico.verificar_retorno(tipo_expressao, token)

            self.consome(Token.ponto_virgula)

            if codigo_expressao:
                self.semantico.gera(indentacao, f'return {codigo_expressao}\n')
            else:
                self.semantico.gera(indentacao, 'return\n')

        elif tipo_token in comandos_possiveis:
            tipo, codigo, _ = self.Expr()
            self.consome(Token.ponto_virgula)
            self.semantico.gera(indentacao, f'{codigo}\n')

        elif tipo_token == Token.ponto_virgula:
            self.consome(Token.ponto_virgula) # Comando vazio
            self.semantico.gera(indentacao, 'pass\n')

        else:
            print(f"Erro Sintático: Comando inválido '{self.token_lido[1]}' na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    # ForStmt -> for ( Expr ; OptExpr ; OptExpr ) Stmt
    def ForStmt (self, indentacao = 1):
        self.consome(Token.for_token)
        self.consome(Token.abre_parentese)
        tipo_init, codigo_init, _ = self.Expr()
        self.consome(Token.ponto_virgula)
        self.semantico.gera(indentacao, f'{codigo_init}\n')

        tipo_cond, codigo_cond, _ = self.OptExpr()
        self.consome(Token.ponto_virgula)

        tipo_incr, codigo_incr, _ = self.OptExpr()
        self.consome(Token.fecha_parentese)

        if codigo_cond:
            self.semantico.gera(indentacao, f'while {codigo_cond}:\n')
        else:
            self.semantico.gera(indentacao, 'while True:\n')

        self.Stmt(indentacao + 1)

        if codigo_incr:
            self.semantico.gera(indentacao + 1, f'{codigo_incr}\n')

    # OptExpr -> Expr | LAMBDA
    def OptExpr (self):
        # Conjunto First da variável OptExpr
        comandos_possiveis = {
            Token.not_token, Token.mais, Token.menos, Token.abre_parentese,
            Token.valor_int, Token.valor_float, Token.valor_char,
            Token.valor_string, Token.identificador
        }

        if self.token_lido[0] in comandos_possiveis:
            return self.Expr() # Retorna a tupla da expressão
        elif self.token_lido[0] in [Token.ponto_virgula, Token.fecha_parentese]:
            return None, '', 'vazio' # Retorna uma tupla vazia
        else:
            print(f"Erro Sintático: Expressão opcional mal formada em 'for' na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    # WhileStmt -> while ( Expr ) Stmt
    def WhileStmt (self, indentacao = 1):
        self.consome(Token.while_token)
        self.consome(Token.abre_parentese)
        tipo, codigo, _ = self.Expr()

        self.consome(Token.fecha_parentese)
        self.semantico.gera(indentacao, f'while {codigo}:\n')

        self.Stmt(indentacao + 1)

    # IfStmt -> if ( Expr ) Stmt ElsePart
    def IfStmt (self, indentacao = 1):
        self.consome(Token.if_token)
        self.consome(Token.abre_parentese)
        tipo, codigo, _ = self.Expr()

        self.consome(Token.fecha_parentese)
        self.semantico.gera(indentacao, f'if {codigo}:\n')

        self.Stmt(indentacao + 1)
        self.ElsePart(indentacao)

    # ElsePart -> else Stmt | LAMBDA
    def ElsePart (self, indentacao = 1):
        if self.token_lido[0] == Token.else_token:
            self.consome(Token.else_token)
            self.semantico.gera(indentacao, 'else:\n')
            self.Stmt(indentacao + 1)
        elif self.token_lido[0] in [
            Token.for_token, Token.while_token, Token.if_token, Token.abre_chave,
            Token.break_token, Token.continue_token, Token.return_token,
            Token.ponto_virgula, Token.int_token, Token.float_token, Token.char_token,
            Token.identificador, Token.valor_int, Token.valor_float, Token.valor_char,
            Token.valor_string, Token.abre_parentese, Token.mais, Token.menos,
            Token.not_token, Token.fecha_chave, Token.eof
        ]:
            pass
        else:
            print(f"Erro Sintático: Cláusula 'else' mal formada na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    # Declaration -> Type IdentList ;
    def Declaration (self, indentacao = 1):
        tipo_variavel = self.Type() # Pegando o tipo da variável atual
        self.IdentList(tipo_variavel, indentacao) # Passando o tipo da lista de variveis
        self.consome(Token.ponto_virgula)

    # Type -> int | float | char
    def Type (self):
        token = self.token_lido[0]
        if token in {Token.int_token, Token.float_token, Token.char_token}:
            self.consome(token)
            return token # Retorna o tipo da variável/função
        else:
            print(f"Erro Sintático: Tipo de dado esperado (int, float, char) na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    # IdentList -> IdentDeclar RestoIdentList
    def IdentList (self, tipo_variavel, indentacao = 1):
        self.IdentDeclar(tipo_variavel, indentacao)
        self.RestoIdentList(tipo_variavel, indentacao)

    # RestoIdentList -> , IdentDeclar RestoIdentList | LAMBDA
    def RestoIdentList (self, tipo_variavel, indentacao = 1):
        if self.token_lido[0] == Token.virgula:
            self.consome(Token.virgula)
            self.IdentDeclar(tipo_variavel, indentacao)
            self.RestoIdentList(tipo_variavel, indentacao)
        elif self.token_lido[0] == Token.ponto_virgula:
            pass
        else:
            print(f"Erro Sintático: Lista de identificadores mal formada na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    # IdentDeclar -> ident OpcIdentDeclar
    def IdentDeclar (self, tipo_variavel, indentacao = 1):
        nome_variavel = self.token_lido[1]
        token = self.token_lido
        self.consome(Token.identificador)
        array, tamanho = self.OpcIdentDeclar() # Pegando se a variável é array e seu tamanho

        self.semantico.declarar_variavel(nome=nome_variavel, tipo=tipo_variavel, array=array, token=token)

        if array:
            self.semantico.gera(indentacao, f'{nome_variavel} = []\n')
        elif tipo_variavel == Token.int_token:
            self.semantico.gera(indentacao, f'{nome_variavel} = 0\n')
        elif tipo_variavel == Token.float_token:
            self.semantico.gera(indentacao, f'{nome_variavel} = 0.0\n')
        elif tipo_variavel == Token.char_token:
            self.semantico.gera(indentacao, f'{nome_variavel} = \'\'\n')

    # OpcIdentDeclar -> [ valorInt ] | LAMBDA
    def OpcIdentDeclar (self):
        if self.token_lido[0] == Token.abre_colchete:
            self.consome(Token.abre_colchete)
            tamanho = self.token_lido[1] # Pegando o tamanho do array
            self.consome(Token.valor_int)
            self.consome(Token.fecha_colchete)
            return True, tamanho # É um array
        elif self.token_lido[0] in [Token.virgula, Token.ponto_virgula]:
            return False, None # Não é um array
        else:
            print(f"Erro Sintático: Declaração de array mal formada na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    # Expr -> Log RestoExpr
    def Expr (self):
        return self.RestoExpr(self.Log()) # Retorna tipo, código e categoria

    # RestoExpr -> = Expr RestoExpr | LAMBDA
    def RestoExpr (self, caracteristicas_esquerdo):
        tipo_esquerdo, codigo_esquerdo, categoria_esquerdo = caracteristicas_esquerdo

        if self.token_lido[0] == Token.atribuicao:
            # Verifica se a categoria do lado esquerdo é possível
            if categoria_esquerdo not in {'identificador', 'acesso_vetor'}:
                raise Exception(f'Erro semântico na linha {self.token_lido[2]}: o lado esquerdo da atribuição deve ser variável ou acesso a vetor.')

            token = self.token_lido
            self.consome(Token.atribuicao)

            # Obtendo os dados do lado direito da atribuição (permite a = b = c)
            tipo_direito, codigo_direito, _ = self.Expr()

            # Validando a atribuição
            self.semantico.validar_atribuicao(tipo_esquerdo, tipo_direito, token)

            novo_codigo = f"{codigo_esquerdo} = {codigo_direito}"

            # Continua a verificar recursivamente
            return self.RestoExpr((tipo_esquerdo, novo_codigo, 'expressao'))

        # Se não for atribuição, retornamos a tupla original da esquerda
        return tipo_esquerdo, codigo_esquerdo, categoria_esquerdo

    # Log -> Nao RestoLog
    def Log (self):
        return self.RestoLog(self.Nao())

    # RestoLog -> AND Nao RestoLog | OR Nao RestoLog | LAMBDA
    def RestoLog (self, caracteristicas_esquerdo):
        tipo_esquerdo, codigo_esquerdo, categoria_esquerdo = caracteristicas_esquerdo
        operador = self.token_lido[0]

        if operador in {Token.and_token, Token.or_token}:
            token = self.token_lido
            self.consome(operador)
            tipo_direito, codigo_direito, _ = self.Nao()

            tipo_resultado = self.semantico.validar_operacao_binaria(tipo_esquerdo, operador, tipo_direito, token)
            novo_codigo = f"{codigo_esquerdo} {Token.msg(operador)} {codigo_direito}"

            return self.RestoLog((tipo_resultado, novo_codigo, 'expressao'))

        return tipo_esquerdo, codigo_esquerdo, categoria_esquerdo

    # Nao -> NOT Nao | Rel
    def Nao (self):
        operador = self.token_lido[0]

        if operador == Token.not_token:
            token = self.token_lido
            self.consome(operador)
            tipo_operando, codigo_operando, _ = self.Nao()

            tipo_resultado = self.semantico.validar_operacao_unaria(operador, tipo_operando, token)
            novo_codigo = f"!{codigo_operando}"

            return tipo_resultado, novo_codigo, 'expressao'
        else:
            return self.Rel()

    # Rel -> Soma RestoRel
    def Rel (self):
        return self.RestoRel(self.Soma())

    # RestoRel -> opRel Soma | LAMBDA
    def RestoRel (self, caracteristicas_esquerdo):
        tipo_esquerdo, codigo_esquerdo, categoria_esquerdo = caracteristicas_esquerdo
        operador = self.token_lido[0]

        if operador == Token.operador_relacional:
            token = self.token_lido
            lexema_operador = token[1]

            self.consome(operador)

            tipo_direito, codigo_direito, _ = self.Soma()

            # Validando semanticamente
            tipo_resultado = self.semantico.validar_operacao_binaria(tipo_esquerdo, operador, tipo_direito, token)

            novo_codigo = f"({codigo_esquerdo} {lexema_operador} {codigo_direito})"

            return tipo_resultado, novo_codigo, 'expressao'

        return tipo_esquerdo, codigo_esquerdo, categoria_esquerdo

    # Soma -> Mult RestoSoma
    def Soma (self):
        return self.RestoSoma(self.Mult())

    # RestoSoma -> + Mult RestoSoma | - Mult RestoSoma | LAMBDA
    def RestoSoma (self, caracteristicas_esquerdo):
        tipo_esquerdo, codigo_esquerdo, categoria_esquerdo = caracteristicas_esquerdo
        operador = self.token_lido[0]

        if operador in {Token.mais, Token.menos}:
            token = self.token_lido
            self.consome(operador)
            tipo_direito, codigo_direito, _ = self.Mult()

            # Validando semanticamente
            tipo_resultado = self.semantico.validar_operacao_binaria(tipo_esquerdo, operador, tipo_direito, token)
            novo_codigo = f"({codigo_esquerdo} {Token.msg(operador)} {codigo_direito})"

            return self.RestoSoma((tipo_resultado, novo_codigo, 'expressao'))

        return tipo_esquerdo, codigo_esquerdo, categoria_esquerdo

    # Mult -> Uno RestoMult
    def Mult (self):
        return self.RestoMult(self.Uno())

    # RestoMult -> * Uno RestoMult | / Uno RestoMult | % Uno RestoMult | LAMBDA
    def RestoMult (self, caracteristicas_esquerdo):
        tipo_esquerdo, codigo_esquerdo, categoria_esquerdo = caracteristicas_esquerdo
        operador = self.token_lido[0]

        op_mult = {Token.multiplicacao, Token.divisao, Token.modulo}

        if operador in op_mult:
            token = self.token_lido
            self.consome(operador)
            tipo_direito, codigo_direito, _ = self.Uno()

            # Validando semanticamente
            tipo_resultado = self.semantico.validar_operacao_binaria(tipo_esquerdo, operador, tipo_direito, token)
            novo_codigo = f"({codigo_esquerdo} {Token.msg(operador)} {codigo_direito})"

            return self.RestoMult((tipo_resultado, novo_codigo, 'expressao'))

        return tipo_esquerdo, codigo_esquerdo, categoria_esquerdo

    # Uno -> + Uno | - Uno | Folha
    def Uno (self):
        operador = self.token_lido[0]
        if operador in {Token.menos, Token.mais}:
            token = self.token_lido
            self.consome(operador)
            tipo_operando, codigo_operando, _ = self.Uno()

            # Validando semanticamente
            tipo_resultado = self.semantico.validar_operacao_unaria(operador, tipo_operando, token)
            novo_codigo = f"({Token.msg(operador)}{codigo_operando})"

            return tipo_resultado, novo_codigo, 'expressao'
        else:
            return self.Folha()

    # Folha -> ( Expr ) | Identifier | valorInt | valorFloat | valorChar | valorString
    def Folha (self):
        token, lexema, linha, _ = self.token_lido
        token_info = self.token_lido

        if token == Token.abre_parentese:
            self.consome(Token.abre_parentese)
            tipo, codigo, _ = self.Expr()
            self.consome(Token.fecha_parentese)
            return tipo, f"({codigo})", 'expressao'

        elif token == Token.identificador:
            simbolo = self.semantico.verificar_identificador_declarado(lexema, token_info)
            self.consome(Token.identificador)
            return self.OpcIdentifier(simbolo)

        elif token == Token.valor_int:
            self.consome(Token.valor_int)
            return (Token.int_token, False), lexema, 'literal'

        elif token == Token.valor_float:
            self.consome(Token.valor_float)
            return (Token.float_token, False), lexema, 'literal'

        elif token == Token.valor_char:
            self.consome(Token.valor_char)
            return (Token.char_token, False), f"\'{lexema}\'", 'literal'

        elif token == Token.valor_string:
            self.consome(Token.valor_string)
            return (Token.char_token, True), f"\"{lexema}\"", 'literal'

        else:
            print(f"Erro Sintático: Expressão esperava um identificador, número ou '(' na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    # OpcIdentifier -> [ Expr ] | ( Params ) | LAMBDA
    def OpcIdentifier (self, simbolo: Simbolo):
        token_info = self.token_lido
        token = token_info[0]

        # Opção 1: acesso a vetor
        if token == Token.abre_colchete:
            if not simbolo.array:
                raise Exception(f"Erro semântico nalinha {token_info[2]}: {simbolo.nome} não é vetor e não pode ser indexado.")

            self.consome(Token.abre_colchete)
            tipo_indice, codigo_indice, _ = self.Expr()

            if tipo_indice != (Token.int_token, False):
                raise Exception(
                    f"Erro semântico nalinha {token_info[2]}: índice do vetor deve ser inteiro.")

            self.consome(Token.fecha_colchete)

            tipo_elemento = (simbolo.tipo, False)
            codigo_acesso = f"{simbolo.nome}[{codigo_indice}]"
            categoria = 'acesso_vetor'

            return tipo_elemento, codigo_acesso, categoria

        # Opção 2: chamada de função
        elif token == Token.abre_parentese:
            if simbolo.categoria != 'funcao':
                raise Exception(
                    f"Erro semântico nalinha {token_info[2]}: {simbolo.nome} não é função e não pode ser chamado.")

            self.consome(Token.abre_parentese)
            tipos_args, codigos_args = self.Params(simbolo)

            self.semantico.validar_chamada_funcao(simbolo, tipos_args, token_info)
            self.consome(Token.fecha_parentese)

            funcoes_padrao = {'putint', 'putfloat', 'putstr', 'putchar', 'getint', 'getfloat', 'getchar'}

            prefixo = ''
            if simbolo.nome not in funcoes_padrao:
                prefixo = 'self.'

            tipo_retorno = (simbolo.tipo, False)
            codigo_chamada = f"{prefixo}{simbolo.nome}({', '.join(codigos_args)})"
            categoria = 'expressao'

            return tipo_retorno, codigo_chamada, categoria

        # Opção 3: uso de variável
        else:
            tipo_variavel = (simbolo.tipo, simbolo.array)
            codigo_variavel = simbolo.nome
            categoria = 'identificador'

            return tipo_variavel, codigo_variavel, categoria

    # Params -> Expr RestoParams | LAMBDA
    def Params (self, simbolo):
        # Conjunto First da variável Params
        comandos_possiveis = {
            Token.not_token, Token.mais, Token.menos, Token.abre_parentese,
            Token.valor_int, Token.valor_float, Token.valor_char,
            Token.valor_string, Token.identificador
        }

        tipos_passados = []
        codigos_passados = []

        if self.token_lido[0] in comandos_possiveis:
            tipo_arg, codigo_arg, _ = self.Expr()
            tipos_passados.append(tipo_arg)
            codigos_passados.append(codigo_arg)
            self.RestoParams(tipos_passados, codigos_passados)

        elif self.token_lido[0] == Token.fecha_parentese:
            pass

        else:
            print(f"Erro Sintático: Parâmetros de função inválidos na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

        return tipos_passados, codigos_passados

    # RestoParams -> , Expr RestoParams | LAMBDA
    def RestoParams (self, tipos_passados, codigos_passados):
        if self.token_lido[0] == Token.virgula:
            self.consome(Token.virgula)
            tipo_arg, codigo_arg, _ = self.Expr()
            tipos_passados.append(tipo_arg)
            codigos_passados.append(codigo_arg)
            self.RestoParams(tipos_passados, codigos_passados)
        elif self.token_lido[0] == Token.fecha_parentese:
            pass
        else:
            print(f"Erro Sintático: Lista de parâmetros mal formada na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception