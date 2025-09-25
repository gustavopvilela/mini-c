from enum import IntEnum

class Token (IntEnum):
    erro = 1
    eof = 2
    identificador = 3
    
    # Valores
    valor_string = 4
    valor_char = 5
    valor_float = 6
    valor_int = 7
    
    # Palavras reservadas
    break_token = 8
    continue_token = 9
    return_token = 10
    for_token = 11
    while_token = 12
    if_token = 13
    else_token = 14
    int_token = 15
    float_token = 16
    char_token = 17
    
    # Operadores
    and_token = 18
    or_token = 19
    not_token = 20
    operador_relacional = 21
    
    # Símbolos
    abre_parentese = 22
    fecha_parentese = 23
    virgula = 24
    abre_colchete = 25
    fecha_colchete = 26
    abre_chave = 27
    fecha_chave = 28
    ponto_virgula = 29
    mais = 30
    menos = 31
    multiplicacao = 32
    divisao = 33
    modulo = 34
    atribuicao = 35
    
    @classmethod
    def msg (cls, token):
        nomes = {
            1: 'erro',
            2: '<eof>',
            3: 'identificador',
            4: 'valor_string',
            5: 'valor_char',
            6: 'valor_float',
            7: 'valor_int',
            8: 'break',
            9: 'continue',
            10: 'return',
            11: 'for',
            12: 'while',
            13: 'if',
            14: 'else',
            15: 'int',
            16: 'float',
            17: 'char',
            18: '&&',
            19: '||',
            20: '!',
            21: 'operador_relacional',
            22: '(',
            23: ')',
            24: ',',
            25: '[',
            26: ']',
            27: '{',
            28: '}',
            29: ';',
            30: '+',
            31: '-',
            32: '*',
            33: '/',
            34: '%',
            35: '=',
        }
        return nomes[token]
    
    @classmethod
    def reservadas (cls, lexema):
        reservadas = {
            'break': Token.break_token,
            'continue': Token.continue_token,
            'for': Token.for_token,
            'while': Token.while_token,
            'if': Token.if_token,
            'else': Token.else_token,
            'return': Token.return_token,
            'int': Token.int_token,
            'float': Token.float_token,
            'char': Token.char_token,
        }
        
        if lexema in reservadas: return reservadas[lexema]
        else: return Token.identificador