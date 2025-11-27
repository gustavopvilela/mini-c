# Trabalho final de *Compiladores I*: Compilador Mini-C

![Comp](https://img.shields.io/badge/IFMG-Compiladores%20I-169873)  [![Python](https://img.shields.io/badge/python-3.13.2-9ebd6e)](https://www.python.org/)

## Introdução

> Um compilador didático para a linguagem **Mini-C**, desenvolvido inteiramente em **Python**.

O projeto realiza a análise léxica, sintática e semântica de códigos fonte escritos em Mini-C e os transpila para **Python**, executando o código resultante automaticamente.

Este trabalho foi desenvolvido pelo aluno Gustavo Henrique Pereira Vilela.

## Sobre o projeto

Este compilador foi construído seguindo os princípios clássicos de construção de compiladores, sem o uso de ferramentas automáticas de geração de parsers (como Yacc ou Bison). Todo o pipeline foi implementado manualmente:

1.  **Scanner (Léxico):** Autômato finito para reconhecimento de tokens.
2.  **Parser (Sintático):** Descida recursiva (*Recursive Descent*) para validação gramatical.
3.  **Semântico & Geração de Código:** Verificação de tipos, escopo e tradução para Python.

O objetivo final é ler um arquivo `.txt` contendo código C simplificado e gerar um arquivo `.py` funcional.



## Funcionalidades da linguagem

A linguagem **Mini-C** suportada por este compilador inclui:

* **Tipos de dados:** `int`, `float`, `char`.
* **Estruturas de controle:**
    * Condicional: `if`, `else`.
    * Repetição: `while`, `for`, `break`, `continue`.
* **Funções:** Declaração de funções com parâmetros e retorno.
* **Vetores:** Declaração e acesso a arrays unidimensionais (ex: `int vetor[10];`).
* **Funções de entrada/saída (built-in):**
    * `putint(x)`, `putfloat(x)`, `putstr(s)`, `putchar(c)`
    * `getint()`, `getfloat()`, `getchar()`


## Arquitetura do compilador

O sistema é dividido em módulos que conversam entre si:

### 1. Análise léxica (`lexico.py`)
Responsável por ler o arquivo fonte caractere por caractere e agrupá-los em **Tokens**.
* Ignora espaços em branco e comentários (`//`).
* Identifica palavras reservadas, operadores, literais e identificadores.
* Usa uma máquina de estados (`estados.py`) para transições.

### 2. Análise sintática (`sintatico.py`)
Recebe os tokens do léxico e verifica se a sequência obedece à gramática da linguagem.
* Implementado via **descida recursiva**.
* Métodos como `Program()`, `Function()`, `Stmt()` representam as regras da gramática.
* Aciona o módulo semântico a cada regra reconhecida.

### 3. Análise semântica (`semantico.py`)
Garante que o código faz sentido lógico (ex: não somar um número com uma string).
* **Tabela de símbolos:** Gerencia escopos e declarações de variáveis/funções.
* **Verificação de tipos:** Valida operações binárias e unárias baseadas em regras rígidas (`tabela_simbolos.py`).
* **Geração de código:** Gera código Python equivalente em tempo real.



## Estrutura de arquivos

```bash
📦 mini-c
 ┣ 📜 main.py              # Ponto de entrada (GUI para seleção de arquivo)
 ┣ 📜 lexico.py            # Analisador Léxico
 ┣ 📜 sintatico.py         # Analisador Sintático
 ┣ 📜 semantico.py         # Analisador Semântico e Gerador de Código
 ┣ 📜 tabela_simbolos.py   # Gerenciamento de tabela de símbolos e regras de tipos
 ┣ 📜 simbolo.py           # Definição da classe Simbolo
 ┣ 📜 estados.py           # Enumeração dos estados do léxico
 ┣ 📜 ttoken.py            # Enumeração dos tipos de Tokens
 ┗ 📜 .gitignore           # Arquivos ignorados pelo git
```

## Como executar

### Pré-requisitos
* **Python 3.x** instalado.
* Biblioteca `tkinter` (geralmente já vem instalada com o Python).

### Passo a passo

1.  Clone o repositório:
    ```bash
    git clone https://github.com/gustavopvilela/mini-c.git
    cd mini-c
    ```

2.  Execute o arquivo principal:
    ```bash
    python main.py
    ```

3.  Uma janela será aberta. Selecione o arquivo de texto (`.txt`) contendo o código Mini-C.

4.  O compilador irá:
    * Gerar o código Python na pasta `compilados/`.
    * Executar o programa automaticamente no terminal.

---

## Exemplo de código

Crie um arquivo chamado `teste.txt` com o seguinte conteúdo para testar:

```c
// Exemplo de Fatorial em Mini-C

int fatorial(int n) {
    if (n < 2) {
        return 1;
    }
    return n * fatorial(n - 1);
}

int main() {
    int num;
    int res;

    putstr("Digite um numero: ");
    num = getint();

    res = fatorial(num);

    putstr("O fatorial e: ");
    putint(res);
    putstr("\n");

    return 0;
}
```

**Saída esperada no terminal**
```
Compilando .../teste.txt
Traduzido com sucesso!

==============================
EXECUTANDO PROGRAMA COMPILADO
==============================

Digite um numero: 5
O fatorial e: 120
```

## Tratamento de erros
O compilador possui um sistema robusto de mensagens de erro. Se houver falhas léxicas, sintáticas ou semânticas (como variáveis não declaradas ou tipos incompatíveis), o processo é interrompido e uma mensagem detalhada é exibida indicando a linha e a coluna do erro.

---

*Feito com ❤️ para o professor Walace.*