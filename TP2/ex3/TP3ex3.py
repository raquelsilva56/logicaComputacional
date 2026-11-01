import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Exercício 3: Multiplicação de inteiros como SFOTS**

    Este exercício parte de um programa imperativo que calcula a multiplicação de dois inteiros não negativos, $a$ e $b$, usando apenas deslocamentos, somas e subtrações. O programa guarda três variáveis, $x$, $y$ e $z$, que começam com os valores $a$, $b$ e $0$. Enquanto $y$ for diferente de zero, repete-se um ciclo:

    se $y$ é par, duplica-se $x$ e divide-se $y$ por dois;
    se $y$ é ímpar, subtrai-se um a $y$ e soma-se $x$ a $z$.

    Quando $y$ chega a zero, o programa termina e $z$ deve ser igual a $a \cdot b$.

    A precisão é limitada a $n$ bits, parâmetro do programa. Por isso tanto o deslocamento de $x$ como a soma $z + x$ podem dar overflow. Isto não se vê no código, mas o diagrama mostra-o explicitamente.

    **O modelo: Control Flow Automaton**

    O prob3.pdf descreve o programa como um **CFA** (Control Flow Automaton), um grafo orientado onde:

    os nodos são ações (init, skip, left, right, stop e error) que atuam sobre os valores das variáveis;

    os ramos transferem o resultado de um nodo para o seguinte, condicionados por uma condição (a ausência de condição equivale a True);
    se um ramo leva a erro, tem precedência sobre os outros; se não houver precedência, a escolha é não determinística;

    o estado do sistema é o identificador do nodo mais o valor das variáveis no input desse nodo.

    A partir de skip há três saídas possíveis: para left se $y \neq 0$ e $y$ é par, para right se $y \neq 0$ e $y$ é ímpar, e para stop se $y = 0$. Tanto left como right podem ir para error em caso de overflow.

    **O que é pedido**

    Pede-se para traduzir este autómato num SFOTS (sistema de transição de estados com fronteira) em Z3, usando BitVec de tamanho $n$, e depois verificar propriedades sobre ele:

    a) construir o SFOTS: identificar as variáveis do modelo, o estado inicial, a relação de transição e o estado de erro;

    b) verificar por $k$-indução que $x \cdot y + z = a \cdot b$ é um invariante;

    c) verificar a segurança do programa: com $a < 2^{n/2}$ e $b < 2^{n/2}$ no estado inicial, o estado de erro nunca é acessível;

    d) a propriedade de animação que exprime que o programa termina quaisquer que sejam $a$ e $b$, e prová-la no SFOTS construído.

    **Cuidado a ter com Z3**

    O Z3 não se comporta como a ALU de um processador:

    todas as operações aritméticas são feitas módulo $2^n$, por isso, por exemplo, $-1$ e $2^n - 1$ são o mesmo valor;

    os operadores <, <=, >, >=, /, % e >> são as versões com sinal; as versões sem sinal são ULT, ULE, UGT, UGE, UDiv, URem e LShR;
    o deslocamento << 1 e a soma são operações totais: nunca assinalam erro e devolvem sempre um valor, mesmo que inesperado.

    Por isso, a deteção de overflow tem de ser implementada no modelo.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Implementação completa(sem testes)**
    """)
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Testes**
    """)
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Justificação de código e testes**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    """)
    return


if __name__ == "__main__":
    app.run()
