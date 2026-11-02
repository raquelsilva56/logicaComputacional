import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import random
    import z3

    return mo, random, z3


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Enunciado
    O Conway’s Game of Life é um exemplo de um autómato celular.  Neste problema modifica-se as regras do autómato de forma a usar um espaço de estados finito.

    1. O espaço de estados é definido por uma grelha de células booleanas (morta = 0/viva = 1) de dimensão $\,N\times N\,$ (com $N > 16$) identificadas por índices $\,(i,j)\in \{1..N\}$.  Estas $\;N^2\;$ células são aqui referidas como “normais”.
    2. Inicialmente todas as células normais estão mortas excepto  as células $\,i,j \leq 3\,$que estão vivas. Um estado onde todas as células normais estão mortas é um “estado de erro”.
    3. Adicionalmente existem :
      1. $\,2\,N+1\,$ “células iniciais” que correspondem a um dos índices, $i$ ou $j$, ser zero. As células iniciais têm valores constantes que, no estado inicial, são gerados aleatoriamente com uma probabilidade $\,1/2\,$ de estarem vivas.
      2. $2N+3\,$”células finais” que não são iniciais e um dos seus índices tem o valor $N+1$. As células finais têm valores constantemente $\,0\,$; i.e. estão mortas.
    4. As células normais do autómato modificam o estado de acordo com a regra “B3|S23”: i.e. a célula nasce (passa de $0$ a $1$) se tem exatamente 3 vizinhos vivos; sobrevive (mantém-se viva) se o número de vizinhos vivos é 2 ou 3 ; caso contrário morre ou continua morta.
    5. A célula $\;(i_0,j_0)\;$e $\,(i_1,j_1)\,$ são vizinhas sse $\;\max(|i_0-i_1|\,,\,|j_0-j_1|)\,=\,1$

    Pretende-se:

    1. Construir uma máquina de estados finita (FSM) que represente este autómato.
      Este problema tem duas interpretações possíveis para as transições da FSM
      1. Em cada transição do sistema uma e só uma célula normal transita de estado.
      2. Em cada transição do sistema todas as células normais transitam de estado simultaneamente.
      Ambas as opções devem ser contempladas e  a relação de transição selecionada é determinada  pelo valor de um parâmetro definido no código.

    2. Provar (ou obter contra-exemplos) as seguintes propriedades:
      1. Nunca se alcança o estado de erro
      2. Nenhuma célula normal está permanentemente morta ou permanentemente viva.
    """)
    return


@app.cell
def _(mo):
    N = 20
    transicao_multipla = mo.ui.switch(label="Transição múltipla")
    passos_slider = mo.ui.slider(
        start=0, stop=8, value=0, label="Passo t para visualizar"
    )
    return N, passos_slider, transicao_multipla


@app.cell
def _(mo, passos_slider, transicao_multipla):
    mo.hstack([transicao_multipla, passos_slider])
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Representação da máquina de estados em Z3
    ### Declaração do estado
    Começamos por criar um a grelha inicial $(N + 2)^2$, com as fronteiras constantes. As células inicias são geradas aleatoriamente com base em `seed`. As células finais são obrigatoriamente mortas. A verificação das células finais deve ocorrer primeiro para garantir que as células nos cantos extremos superior direito e inferior esquero estejam mortas.
    """)
    return


@app.cell
def _(N, random, z3):
    def criar_estado(t, seed=2112026):
        rng = random.Random(seed)
        e = {}
        for r in range(N + 2):
            for c in range(N + 2):
                if r == N + 1 or c == N + 1:
                    # 2N + 3 celulas finais sempre mortas
                    e[(r, c)] = z3.BoolVal(False)

                elif r == 0 or c == 0:
                    # 2N + 1 celulas iniciais com probabilidade 1/2 de estarem vivas ou mortas
                    viva = rng.choice([True, False])
                    e[(r, c)] = z3.BoolVal(viva)

                else:
                    # N * N células normais variadas no período t
                    e[(r, c)] = z3.Bool(f"c_{t}_{r}_{c}")

        return e

    return (criar_estado,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Estado inicial e estado de erro
    Conforme especificado no enunciado, o estado inicial $e_0$ contém todas as células normais mortas, com exceção daquelas com ambos os índices $\leq 3$. O estado de erro é definido como o estado em que todas as célulsa normais estão mortas.
    """)
    return


@app.cell
def _(N, z3):
    def estado_inicial(e):
        return z3.And(
            [
                e[(r, c)] == (r <= 3 and c <= 3)
                for r in range(1, N + 1)
                for c in range(1, N + 1)
            ]
        )

    def estado_erro(e):
        return z3.And(
            [
                z3.Not(e[(r, c)])
                for r in range(1, N + 1)
                for c in range(1, N + 1)
            ]
        )

    return (estado_inicial,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Transições
    A regra de transição (B3|S23) especifica o comportamento de cada célula individual, definindo as condições necessárias para que uma célula nasça e continue viva. Definimos então o comportamento de cada passo de transição "ponto-a-ponto":
    """)
    return


@app.cell
def _(z3):
    def b3_s23(e, r, c):
        vizinhanca = [
            e[(r + dr, c + dc)]
            for dr in [-1, 0, 1]
            for dc in [-1, 0, 1]
            if dr != 0 or dc != 0  # nao coletar a si mesma
        ]

        # nao há conversao automatica Bool -> Int
        vizinhos_vivos = z3.Sum(z3.If(v, 1, 0) for v in vizinhanca)

        # nasce ou sobrevive se tiver 3 vizinhos; sobrevive se tiver dois vizinhos
        return z3.Or(
            vizinhos_vivos == 3, z3.And(e[(r, c)], vizinhos_vivos == 2)
        )

    return (b3_s23,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Podemos então definir a relação de transição entre dois estados $e_0$ e $e_1$:
    + No caso de múltiplas transições, a condição de cada célula do estado $e_1$ deve representar a situação daquela mesma célula no estado $e_0$ depois da aplicação da regra B3|S23.
    + No caso de transições singulares, precisamos verificar que $e_1$ só difere de $e_0$ a menos da situação de uma única célula.
    """)
    return


@app.cell
def _(N, b3_s23, z3):
    def transicao(e0, e1, multipla=True):
        if multipla:
            return z3.And(
                [
                    e1[(r, c)] == b3_s23(e0, r, c)
                    for r in range(1, N + 1)
                    for c in range(1, N + 1)
                ]
            )
        else:
            # todas as celulas do estado mais recente mantem seu valor, ou atualizam o valor do estado passado
            celulas_validas = [
                z3.If(
                    e1[(r, c)] != e0[(r, c)],
                    e1[(r, c)] == b3_s23(e0, r, c),
                    True,
                )
                for r in range(1, N + 1)
                for c in range(1, N + 1)
            ]

            num_mudancas = z3.Sum(
                [
                    z3.If(e1[(r, c)] != e0[(r, c)], 1, 0)
                    for r in range(1, N + 1)
                    for c in range(1, N + 1)
                ]
            )

        return z3.And(num_mudancas == 1, *celulas_validas)

    return (transicao,)


@app.cell
def _(
    N,
    criar_estado,
    estado_inicial,
    passos_slider,
    transicao,
    transicao_multipla,
    z3,
):
    def desenha_estado(e, m=None):
        linhas = []
        for r in range(N + 2):
            linha = []
            for c in range(N + 2):
                val = (
                    e[(r, c)]
                    if m is None
                    else m.eval(e[(r, c)], model_completion=True)
                )
                viva = z3.is_true(z3.simplify(val))
                linha.append("V" if viva else "M")
            linhas.append(" ".join(linha))
        return "\n".join(linhas)

    K_max = passos_slider.stop
    s_sim = z3.Solver()
    estados = [criar_estado(t) for t in range(K_max + 1)]

    s_sim.add(estado_inicial(estados[0]))
    for t in range(K_max):
        s_sim.add(
            transicao(
                estados[t], estados[t + 1], multipla=transicao_multipla.value
            )
        )

    if s_sim.check() == z3.sat:
        modelo = s_sim.model()
        t_atual = passos_slider.value
        print(desenha_estado(estados[t_atual], modelo))

    else:
        print("error")
    return


if __name__ == "__main__":
    app.run()
