from lexico import Lexico
from sintatico import Sintatico
from ttoken import Token

if __name__ == '__main__':
    try:
        with open("testes/teste.txt", 'r', encoding='utf-8') as arquivo:
            lexico = Lexico(arquivo)
            sintatico = Sintatico(lexico)
            sintatico.testa_lexico()

    except FileNotFoundError:
        print(f"Erro: O arquivo '{arquivo}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")