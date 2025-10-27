from lexico import Lexico
from semantico import Semantico
from sintatico import Sintatico
from ttoken import Token

if __name__ == '__main__':
    try:
        with open("testes/teste_com_erros.txt", 'r', encoding='utf-8') as arquivo:
            lexico = Lexico(arquivo)
            sintatico = Sintatico(lexico)
            sintatico.traduz()

    except FileNotFoundError:
        print(f"Erro: O arquivo '{arquivo}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")