import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog

from lexico import Lexico
from sintatico import Sintatico

def selecionar_arquivo ():
    root = tk.Tk()
    root.withdraw()
    caminho_arquivo = filedialog.askopenfilename(
        title="Selecione o arquivo de código Mini-C",
        filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")]
    )
    return caminho_arquivo

def criar_pasta_compilados (nome_pasta: str = "compilados"):
    if not os.path.exists(nome_pasta):
        os.makedirs(nome_pasta)
    return nome_pasta

def gerar_nome_saida (caminho_entrada, pasta_saida):
    nome_arquivo = os.path.basename(caminho_entrada)
    nome_base = os.path.splitext(nome_arquivo)[0]
    caminho_saida = os.path.join(pasta_saida, f'{nome_base}.py')
    return caminho_saida

if __name__ == '__main__':
    caminho_entrada = selecionar_arquivo()

    if not caminho_entrada:
        print("Nenhum arquivo selecionado.")
        exit()

    pasta_saida = criar_pasta_compilados()
    caminho_saida = gerar_nome_saida(caminho_entrada, pasta_saida)

    print(f'Compilando {caminho_entrada}')
    print(f'Destino: {pasta_saida}')

    try:
        with open(caminho_entrada, 'r', encoding='utf-8') as arquivo:
            lexico = Lexico(arquivo)
            sintatico = Sintatico(lexico, alvo=caminho_saida)
            sucesso = sintatico.traduz()
            sintatico.semantico.finaliza()

        if sucesso:
            print('\n' + '='*30)
            print("EXECUTANDO PROGRAMA COMPILADO")
            print('='*30 + '\n')

            # Executando o programa compilado
            subprocess.run([sys.executable, caminho_saida])
        else:
            if os.path.exists(caminho_saida):
                try:
                    os.remove(caminho_saida)
                except Exception as ex:
                    print(f'\nErro de compilação.Não foi possível excluir o arquivo gerado: {ex}')
    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_entrada}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")