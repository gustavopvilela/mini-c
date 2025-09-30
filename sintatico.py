from ttoken import Token
from lexico import Lexico

class Sintatico:
    def __init__(self, lexico: Lexico):
        self.lexico = lexico
        self.token_lido = None

    def traduz(self):
        self.token_lido = self.lexico.get_token()
        try:
            self.Program()
            self.consome(Token.eof)
            print("Traduzido com sucesso!")
        except:
            print("Ocorreu um erro durante a tradução.")

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
            pass
        else:
            print(f"Erro Sintático: Início de programa inesperado com o token '{self.token_lido[1]}' na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    # Function -> Type ident ( ArgList ) CompoundStmt
    def Function (self):
        self.Type()
        self.consome(Token.funcao)
        self.consome(Token.abre_parentese)
        self.ArgList()
        self.consome(Token.fecha_parentese)
        self.CompoundStmt()

    # ArgList -> Arg RestoArgList | LAMBDA
    def ArgList (self):
        if self.token_lido[0] in [Token.int_token, Token.float_token, Token.char_token]:
            self.Arg()
            self.RestoArgList()
        elif self.token_lido[0] == Token.fecha_parentese:
            pass
        else:
            print(f"Erro Sintático: Lista de argumentos inválida na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    # RestoArgList -> , Arg RestoArgList | LAMBDA
    def RestoArgList (self):
        if self.token_lido[0] == Token.virgula:
            self.consome(Token.virgula)
            self.Arg()
            self.RestoArgList()
        elif self.token_lido[0] == Token.fecha_parentese:
            pass
        else:
            print(f"Erro Sintático: Argumento adicional mal formado na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    # Arg -> Type IdentArg
    def Arg (self):
        self.Type()
        self.IdentArg()

    # IdentArg -> ident OpcIdentArg
    def IdentArg (self):
        self.consome(Token.identificador)
        self.OpcIdentArg()

    # OpcIdentArg -> [ ] | LAMBDA
    def OpcIdentArg (self):
        if self.token_lido[0] == Token.abre_colchete:
            self.consome(Token.abre_colchete)
            self.consome(Token.fecha_colchete)
        elif self.token_lido[0] in [Token.virgula, Token.fecha_parentese]:
            pass
        else:
            print(f"Erro Sintático: Argumento de array mal formado na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    # CompoundStmt -> { StmtList }
    def CompoundStmt(self):
        self.consome(Token.abre_chave)
        self.StmtList()
        self.consome(Token.fecha_chave)

    # StmtList -> Stmt StmtList | LAMBDA
    def StmtList(self):
        comandos_possiveis = [
            Token.for_token, Token.while_token, Token.if_token, Token.abre_chave,
            Token.break_token, Token.continue_token, Token.return_token, Token.ponto_virgula,
            Token.int_token, Token.float_token, Token.char_token, Token.identificador,
            Token.valor_int, Token.valor_float, Token.valor_char, Token.valor_string,
            Token.abre_parentese, Token.mais, Token.menos, Token.not_token
        ]

        if self.token_lido[0] in comandos_possiveis:
            self.Stmt()
            self.StmtList()
        elif self.token_lido[0] == Token.fecha_chave:
            pass
        else:
            print(f"Erro Sintático: Declaração ou expressão inválida na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    def Stmt (self):
        tipo_token = self.token_lido[0]

        if tipo_token == Token.for_token: self.ForStmt()
        elif tipo_token == Token.while_token: self.WhileStmt()
        elif tipo_token == Token.if_token: self.IfStmt()
        elif tipo_token == Token.abre_chave: self.CompoundStmt()
        elif tipo_token == Token.break_token:
            self.consome(Token.break_token)
            self.consome(Token.ponto_virgula)
        elif tipo_token == Token.continue_token:
            self.consome(Token.continue_token)
            self.consome(Token.ponto_virgula)
        elif tipo_token == Token.return_token:
            self.consome(Token.return_token)
            self.Expr()
            self.consome(Token.ponto_virgula)
        elif tipo_token in [Token.int_token, Token.float_token, Token.char_token]:
            self.Declaration()
        elif tipo_token == Token.ponto_virgula:
            self.consome(Token.ponto_virgula)
        elif tipo_token in [Token.identificador, Token.valor_int, Token.valor_float, Token.valor_char, Token.valor_string, Token.abre_parentese, Token.mais, Token.menos, Token.not_token]:
            self.Expr()
            self.consome(Token.ponto_virgula)
        else:
            print(f"Erro Sintático: Comando inválido '{self.token_lido[1]}' na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    # ForStmt -> for ( Expr ; OptExpr ; OptExpr ) Stmt
    def ForStmt (self):
        self.consome(Token.for_token)
        self.consome(Token.abre_parentese)
        self.Expr()
        self.consome(Token.ponto_virgula)
        self.OptExpr()
        self.consome(Token.ponto_virgula)
        self.OptExpr()
        self.consome(Token.fecha_parentese)
        self.Stmt()

    # OptExpr -> Expr | LAMBDA
    def OptExpr (self):
        if self.token_lido[0] in [Token.identificador, Token.valor_int, Token.valor_float, Token.valor_char, Token.valor_string, Token.abre_parentese, Token.mais, Token.menos, Token.not_token]:
            self.Expr()
        elif self.token_lido[0] in [Token.ponto_virgula, Token.fecha_parentese]:
            pass
        else:
            print(f"Erro Sintático: Expressão opcional mal formada em 'for' na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    # WhileStmt -> while ( Expr ) Stmt
    def WhileStmt (self):
        self.consome(Token.while_token)
        self.consome(Token.abre_parentese)
        self.Expr()
        self.consome(Token.fecha_parentese)
        self.Stmt()

    # IfStmt -> if ( Expr ) Stmt ElsePart
    def IfStmt (self):
        self.consome(Token.if_token)
        self.consome(Token.abre_parentese)
        self.Expr()
        self.consome(Token.fecha_parentese)
        self.Stmt()
        self.ElsePart()

    # ElsePart -> else Stmt | LAMBDA
    def ElsePart (self):
        if self.token_lido[0] == Token.else_token:
            self.consome(Token.else_token)
            self.Stmt()
        elif self.token_lido[0] in [Token.for_token, Token.while_token, Token.if_token, Token.abre_chave, Token.break_token, Token.continue_token, Token.return_token, Token.ponto_virgula, Token.int_token, Token.float_token, Token.char_token, Token.identificador, Token.valor_int, Token.valor_float, Token.valor_char, Token.valor_string, Token.abre_parentese, Token.mais, Token.menos, Token.not_token, Token.fecha_chave, Token.eof]:
            pass
        else:
            print(f"Erro Sintático: Cláusula 'else' mal formada na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    # Declaration -> Type IdentList ;
    def Declaration (self):
        self.Type()
        self.IdentList()
        self.consome(Token.ponto_virgula)

    # Type -> int | float | char
    def Type (self):
        if self.token_lido[0] == Token.int_token: self.consome(Token.int_token)
        elif self.token_lido[0] == Token.float_token: self.consome(Token.float_token)
        elif self.token_lido[0] == Token.char_token: self.consome(Token.char_token)
        else:
            print(f"Erro Sintático: Tipo de dado esperado (int, float, char) na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    # IdentList -> IdentDeclar RestoIdentList
    def IdentList (self):
        self.IdentDeclar()
        self.RestoIdentList()

    # RestoIdentList -> , IdentDeclar RestoIdentList | LAMBDA
    def RestoIdentList (self):
        if self.token_lido[0] == Token.virgula:
            self.consome(Token.virgula)
            self.IdentDeclar()
            self.RestoIdentList()
        elif self.token_lido[0] == Token.ponto_virgula:
            pass
        else:
            print(f"Erro Sintático: Lista de identificadores mal formada na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    # IdentDeclar -> ident OpcIdentDeclar
    def IdentDeclar (self):
        self.consome(Token.identificador)
        self.OpcIdentDeclar()

    # OpcIdentDeclar -> [ valorInt ] | LAMBDA
    def OpcIdentDeclar (self):
        if self.token_lido[0] == Token.abre_colchete:
            self.consome(Token.abre_colchete)
            self.consome(Token.valor_int)
            self.consome(Token.fecha_colchete)
        elif self.token_lido[0] in [Token.virgula, Token.ponto_virgula]:
            pass
        else:
            print(f"Erro Sintático: Declaração de array mal formada na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    # Expr -> Log RestoExpr
    def Expr (self):
        self.Log()
        self.RestoExpr()

    # RestoExpr -> = Expr RestoExpr | LAMBDA
    def RestoExpr (self):
        if self.token_lido[0] == Token.atribuicao:
            self.consome(Token.atribuicao)
            self.Expr()
            self.RestoExpr()
        elif self.token_lido[0] in [Token.virgula, Token.fecha_colchete, Token.fecha_parentese, Token.ponto_virgula]:
            pass
        else:
            print(f"Erro Sintático: Atribuição mal formada na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    # Log -> Nao RestoLog
    def Log (self):
        self.Nao()
        self.RestoLog()

    # RestoLog -> AND Nao RestoLog | OR Nao RestoLog | LAMBDA
    def RestoLog (self):
        if self.token_lido[0] == Token.and_token:
            self.consome(Token.and_token)
            self.Nao()
            self.RestoLog()
        elif self.token_lido[0] == Token.or_token:
            self.consome(Token.or_token)
            self.Nao()
            self.RestoLog()
        elif self.token_lido[0] in [Token.atribuicao, Token.virgula, Token.fecha_colchete, Token.fecha_parentese, Token.ponto_virgula]:
            pass
        else:
            print(f"Erro Sintático: Operador lógico (&&, ||) mal formado na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    # Nao -> NOT Nao | Rel
    def Nao (self):
        if self.token_lido[0] == Token.not_token:
            self.consome(Token.not_token)
            self.Nao()
        else:
            self.Rel()

    # Rel -> Soma RestoRel
    def Rel (self):
        self.Soma()
        self.RestoRel()

    # RestoRel -> opRel Soma | LAMBDA
    def RestoRel (self):
        if self.token_lido[0] == Token.operador_relacional:
            self.consome(Token.operador_relacional)
            self.Soma()
        elif self.token_lido[0] in [Token.and_token, Token.or_token, Token.atribuicao, Token.virgula, Token.fecha_colchete, Token.fecha_parentese, Token.ponto_virgula]:
            pass
        else:
            print(f"Erro Sintático: Operador relacional mal formado na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    # Soma -> Mult RestoSoma
    def Soma (self):
        self.Mult()
        self.RestoSoma()

    # RestoSoma -> + Mult RestoSoma | - Mult RestoSoma | LAMBDA
    def RestoSoma (self):
        if self.token_lido[0] == Token.mais:
            self.consome(Token.mais)
            self.Mult()
            self.RestoSoma()
        elif self.token_lido[0] == Token.menos:
            self.consome(Token.menos)
            self.Mult()
            self.RestoSoma()
        elif self.token_lido[0] in [Token.operador_relacional, Token.and_token, Token.or_token, Token.atribuicao, Token.virgula, Token.fecha_colchete, Token.fecha_parentese, Token.ponto_virgula]:
            pass
        else:
            print(f"Erro Sintático: Operador de soma/subtração mal formado na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    # Mult -> Uno RestoMult
    def Mult (self):
        self.Uno()
        self.RestoMult()

    # RestoMult -> * Uno RestoMult | / Uno RestoMult | % Uno RestoMult | LAMBDA
    def RestoMult (self):
        if self.token_lido[0] == Token.multiplicacao:
            self.consome(Token.multiplicacao)
            self.Uno()
            self.RestoMult()
        elif self.token_lido[0] == Token.divisao:
            self.consome(Token.divisao)
            self.Uno()
            self.RestoMult()
        elif self.token_lido[0] == Token.modulo:
            self.consome(Token.modulo)
            self.Uno()
            self.RestoMult()
        elif self.token_lido[0] in [
            Token.mais, Token.menos, Token.operador_relacional, Token.and_token,
            Token.or_token, Token.atribuicao, Token.virgula, Token.fecha_colchete,
            Token.fecha_parentese, Token.ponto_virgula
        ]:
            pass
        else:
            print(f"Erro Sintático: Operador de multiplicação/divisão mal formado na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    # Uno -> + Uno | - Uno | Folha
    def Uno (self):
        if self.token_lido[0] == Token.mais:
            self.consome(Token.mais)
            self.Uno()
        elif self.token_lido[0] == Token.menos:
            self.consome(Token.menos)
            self.Uno()
        else:
            self.Folha()

    # Folha -> ( Expr ) | Identifier | valorInt | valorFloat | valorChar | valorString
    def Folha (self):
        if self.token_lido[0] == Token.abre_parentese:
            self.consome(Token.abre_parentese)
            self.Expr()
            self.consome(Token.fecha_parentese)
        elif self.token_lido[0] == Token.identificador: self.Identifier()
        elif self.token_lido[0] == Token.valor_int: self.consome(Token.valor_int)
        elif self.token_lido[0] == Token.valor_float: self.consome(Token.valor_float)
        elif self.token_lido[0] == Token.valor_char: self.consome(Token.valor_char)
        elif self.token_lido[0] == Token.valor_string: self.consome(Token.valor_string)
        else:
            print(f"Erro Sintático: Expressão esperava um identificador, número ou '(' na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    # Identifier -> ident OpcIdentifier
    def Identifier (self):
        self.consome(Token.identificador)
        self.OpcIdentifier()

    # OpcIdentifier -> [ Expr ] | ( Params ) | LAMBDA
    def OpcIdentifier (self):
        if self.token_lido[0] == Token.abre_colchete:
            self.consome(Token.abre_colchete)
            self.Expr()
            self.consome(Token.fecha_colchete)
        elif self.token_lido[0] == Token.abre_parentese:
            self.consome(Token.abre_parentese)
            self.Params()
            self.consome(Token.fecha_parentese)
        elif self.token_lido[0] in [Token.multiplicacao, Token.divisao, Token.modulo, Token.mais, Token.menos, Token.operador_relacional, Token.and_token, Token.or_token, Token.atribuicao, Token.virgula, Token.fecha_colchete, Token.fecha_parentese, Token.ponto_virgula]:
            pass
        else:
            print(f"Erro Sintático: Uso inválido de identificador (esperava-se '(', '[' ou operador) na linha {self.token_lido[2]}, coluna {self.token_lido[3]})")
            raise Exception

    # Params -> Expr RestoParams | LAMBDA
    def Params (self):
        if self.token_lido[0] in [Token.identificador, Token.valor_int, Token.valor_float, Token.valor_char, Token.valor_string, Token.abre_parentese, Token.mais, Token.menos, Token.not_token]:
            self.Expr()
            self.RestoParams()
        elif self.token_lido[0] == Token.fecha_parentese:
            pass
        else:
            print(f"Erro Sintático: Parâmetros de função inválidos na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception

    # RestoParams -> , Expr RestoParams | LAMBDA
    def RestoParams (self):
        if self.token_lido[0] == Token.virgula:
            self.consome(Token.virgula)
            self.Expr()
            self.RestoParams()
        elif self.token_lido[0] == Token.fecha_parentese:
            pass
        else:
            print(f"Erro Sintático: Lista de parâmetros mal formada na linha {self.token_lido[2]}, coluna {self.token_lido[3]}")
            raise Exception