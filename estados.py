from enum import Enum

class Estado (Enum):
    INICIAL = 1
    IDENTIFICADOR = 2
    VALOR_INT = 3
    VALOR_FLOAT = 4
    VALOR_STRING = 5
    VALOR_CHAR = 6
    OP_REL_MAIOR = 7
    OP_REL_MENOR = 8
    OP_REL_IGUAL = 9
    OP_REL_DIFERENTE = 10
    AND = 12
    OR = 13