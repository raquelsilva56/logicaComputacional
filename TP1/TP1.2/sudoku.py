import marimo

__generated_with = "0.25.1"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    1. representa qualquer **grupo de células com restrição "todos
           diferentes"** através de uma classe genérica (secção
           "`box` — grupo genérico de células"(R1)).
    """)
    return


@app.class_definition
class Grupo:
    """Conjunto de células com a restrição 'todos diferentes'.
    Guarda (linha, coluna)->valor fixo, ou None se a célula for livre."""

    def __init__(self, n, cells=None):
        self.n = n
        self.N = n * n
        self.cells = {}
        if cells is not None:
            for (i, j), val in cells.items():
                self.add(i, j, val)

    def add(self, i, j, val=None):
        if not (0 <= i < self.N and 0 <= j < self.N):
            raise ValueError(f"Célula ({i}, {j}) fora da grelha")
        if val is not None and not (1 <= val <= self.N):
            raise ValueError(f"Valor {val} fora de [1, {self.N}]")
        self.cells[(i, j)] = val

    def matrix(self):
        m = [[0] * self.N for _ in range(self.N)]
        for (i, j), val in self.cells.items():
            if val is not None:
                m[i][j] = val
        return m


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Célula de teste de R1**, o resultado é o esperado.
    Como o enunciado pede para que o notebook teste automaticamente com n diferentes, achamos que valia a pena acrescentar o caso n=2 à célula de teste R1.
    """)
    return


@app.cell
def _(mo):
    _g = Grupo(3)
    _g.add(0, 0, 5)
    _g.add(1, 1)   #célula livre

    _erros = []
    for _i, _j, _v in [(9, 0, None), (0, 0, 10), (-1, 2, 3)]:
        try:
            _g.add(_i, _j, _v)
            _erros.append(f"({_i},{_j},{_v}) não foi rejeitado")
        except ValueError:
            pass

    _g2 = Grupo(2)
    _g2.add(3, 3, 4)   # tem de aceitar
    try:
        _g2.add(4, 0)
        _erros.append("(4,0) com n=2 NÃO foi rejeitado")
    except ValueError:
        pass

    mo.callout(
        mo.md(f"cells = `{_g.cells}`  \nprimeira linha = `{_g.matrix()[0]}`" 
              + ("" if not _erros else f"  \n**Falhas:** {_erros}")),
        kind="success" if not _erros else "danger",
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## R1: `Grupo` (grupo genérico de células)

    **Correspondência com o enunciado:** `box` → `Grupo`. Escolhemos este nome porque
    a classe representa um *grupo de células* sujeito à restrição "todos diferentes",
    e não a grelha em si.

    **Ideia central.** Num Sudoku a regra é sempre a mesma: um conjunto de células
    tem de ter valores todos diferentes. O que muda entre uma linha, uma coluna e um
    bloco é apenas *que células pertencem ao conjunto*. Por isso `Grupo` só sabe
    guardar "um conjunto de células, algumas já fixas", e não sabe nada sobre linhas,
    colunas, blocos ou Sudoku. É esta generalidade que permite tratar todos os
    grupos da mesma forma e acrescentar variantes (diagonais,
    regiões irregulares) sem alterar o modelo.

    **Estrutura de dados.** Usamos um dicionário `(linha, coluna) → valor | None`:

    - a chave identifica a célula e o valor distingue *célula fixa* (inteiro) de
      *célula livre* (`None`), que é exatamente a informação que o enunciado pede;
    - só guarda as células que pertencem ao grupo. Um grupo tem tipicamente $n^2$
      células, muito menos do que as $n^4$ da grelha, por isso uma matriz $n^2 \times n^2$
      por grupo desperdiçaria memória;
    - acesso e inserção em tempo médio constante, e uma célula repetida limita-se a
      sobrescrever a entrada anterior em vez de ficar duplicada.

    **Parametrização.** A classe guarda `n` e calcula `N = n²` uma única vez. Todos os
    limites (coordenadas em $[0, N-1]$, valores em $[1, N]$) dependem de `N`, e nunca
    de um `9` escrito no código. Isto garante que funciona para qualquer $n$
    (testado com $n=2$ e $n=3$).

    **Validação.** O método `add` rejeita, com `ValueError`, coordenadas fora da
    grelha e valores fora de $[1, n^2]$, e só depois guarda a célula. Assim, um grupo
    nunca fica num estado inválido. O construtor, quando recebe um conjunto inicial
    de células, chama `add` para cada uma, de modo que a validação existe num único
    sítio e não há maneira de contornar as regras pelo construtor.

    **Representação matricial.** `matrix()` devolve uma matriz $n^2 \times n^2$ com
    o valor fixo nas células fixas e `0` em todas as outras (células livres e células
    fora do grupo). Aqui perde-se a distinção entre "livre" e "não pertence" sendo intencional: a matriz serve para mostrar valores, e a distinção continua
    disponível no dicionário `cells`, que é o que o modelo CSP usa.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **R2.** Um grupo que representa o **bloco $n \times n$** cujo
          canto superior esquerdo é a célula $(i \cdot n,\ j \cdot n)$,
          parametrizado pelos índices de bloco $(i, j)$ com $0 \le i, j <
          n$.
    """)
    return


@app.class_definition
class Cube(Grupo):
    """Bloco nxn de índices (bi, bj); canto superior esquerdo em (bi*n, bj*n)"""

    def __init__(self, n, bi, bj):
        super().__init__(n)
        if not (0 <= bi < n and 0 <= bj < n):
            raise ValueError(f"Bloco ({bi}, {bj}) fora de [0, {n})")
        for di in range(n):
            for dj in range(n):
                self.add(bi * n + di, bj * n + dj)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Célula de teste R2**
    """)
    return


@app.cell
def _(mo):
    _b = Cube(3, 1, 2)
    assert len(_b.cells) == 9
    assert min(i for i, _ in _b.cells) == 3 and max(i for i, _ in _b.cells) == 5
    assert min(j for _, j in _b.cells) == 6 and max(j for _, j in _b.cells) == 8

    _b2 = Cube(2, 1, 1)
    assert sorted(_b2.cells) == [(2, 2), (2, 3), (3, 2), (3, 3)]

    try:
        Cube(3, 3, 0)
        _rejeitou = False
    except ValueError:
        _rejeitou = True
    assert _rejeitou

    mo.callout(mo.md("`Cube` OK para $n=3$, $n=2$ e rejeita blocos inválidos."), kind="success")
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## R2: `Cube` (bloco $n \times n$)

    **Correspondência com o enunciado:** `cube` → `Cube`.

    **Ideia principal** Um bloco $n \times n$ é só um grupo de células, por isso `Cube`
    herda de `Grupo`. A herança é adequada porque um `Cube` é um `Grupo`
    (tudo o que se pode fazer com um grupo faz-se com um bloco) e porque o modelo
    CSP vai tratá-lo exatamente como qualquer outro grupo, sem precisar de saber
    que é um bloco.

    **Construção.** O bloco de índices $(b_i, b_j)$, com $0 \le b_i, b_j < n$, tem o
    canto superior esquerdo em $(b_i \cdot n,\ b_j \cdot n)$. O construtor chama
    `super().__init__(n)` para criar o grupo vazio e depois percorre os
    deslocamentos $d_i, d_j \in [0, n)$, adicionando a célula
    $(b_i \cdot n + d_i,\ b_j \cdot n + d_j)$. São $n^2$ células, que é precisamente
    o tamanho de um bloco e o número de valores distintos que o bloco tem de conter.

    **Reutilização e validação.** `Cube` não repete nenhuma lógica de `Grupo`:
    usa `add`, que já valida as coordenadas. Acrescentamos apenas a validação de
    $(b_i, b_j)$, porque sem ela um índice de bloco inválido seria rejeitado pelo
    `add` com uma mensagem sobre uma *célula* fora da grelha.

    **Generalidade.** Nada no código assume $n = 3$: os índices e o tamanho do
    bloco dependem só de $n$. Para $n=2$ obtêm-se 4 blocos $2 \times 2$ numa
    grelha $4 \times 4$, e para $n=3$ obtêm-se 9 blocos $3 \times 3$ numa grelha
    $9 \times 9$ (ambos verificados nos testes).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **R3.** **Path**: Um grupo que representa o **troço reto** (horizontal ou
          vertical) de células entre duas coordenadas `inicio` e `fim`,
          inclusive — tem de funcionar tanto para `fim` "depois" de
          `inicio` como "antes" (ou seja, percorrer a sequência em
          qualquer sentido).
    """)
    return


@app.class_definition
class Path(Grupo):
    """Troço reto (horizontal ou vertical) de inicio a fim, em qualquer sentido."""

    def __init__(self, n, inicio, fim):
        super().__init__(n)
        (i0, j0), (i1, j1) = inicio, fim
        if i0 != i1 and j0 != j1:
            raise ValueError("inicio e fim têm de estar na mesma linha ou coluna")

        def _sinal(x):
            return (x > 0) - (x < 0)

        di, dj = _sinal(i1 - i0), _sinal(j1 - j0)
        tamanho = max(abs(i1 - i0), abs(j1 - j0)) + 1
        for k in range(tamanho):
            self.add(i0 + k * di, j0 + k * dj)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Célula de teste R3**
    """)
    return


@app.cell
def _(mo):
    # horizontal, sentido inverso
    assert list(Path(3, (0, 5), (0, 2)).cells) == [(0, 5), (0, 4), (0, 3), (0, 2)]
    # vertical, sentido normal
    assert list(Path(3, (2, 1), (5, 1)).cells) == [(2, 1), (3, 1), (4, 1), (5, 1)]
    # célula única
    assert list(Path(3, (4, 4), (4, 4)).cells) == [(4, 4)]
    # linha completa com n=2
    assert len(Path(2, (1, 0), (1, 3)).cells) == 4

    for _ini, _fim in [((0, 0), (1, 1)), ((0, 0), (0, 9))]:   # diagonal, fora da grelha
        try:
            Path(3, _ini, _fim)
            raise AssertionError(f"{_ini}->{_fim} devia ser rejeitado")
        except ValueError:
            pass

    mo.callout(mo.md("`Path` OK nos dois sentidos, horizontal e vertical, e rejeita casos inválidos."), kind="success")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
 
    """)
    return


@app.cell
def _():
    import random

    def pistas(n, k=None, rng=random):
        """Grupo com k células escolhidas ao acaso, cada uma fixa a um valor aleatório.
        Os valores são todos distintos (por isso k <= N)."""
        N = n * n
        if k is None:
            k = n
        if not (0 <= k <= N):
            raise ValueError(f"k={k} fora de [0, {N}]")
        posicoes = [(i, j) for i in range(N) for j in range(N)]
        escolhidas = rng.sample(posicoes, k)
        valores = rng.sample(range(1, N + 1), k)
        g = Grupo(n)
        for (i, j), v in zip(escolhidas, valores):
            g.add(i, j, v)
        return g

    return (pistas,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Célula Teste R4**
    """)
    return


@app.cell
def _(mo, pistas):
    for _n in (2, 3):
        _g = pistas(_n)
        assert len(_g.cells) == _n                       # k por omissão = n
        assert all(v is not None for v in _g.cells.values())
        _vals = list(_g.cells.values())
        assert len(set(_vals)) == len(_vals)             # valores distintos
        assert all(1 <= v <= _n * _n for v in _vals)
    assert len(pistas(3, k=9).cells) == 9                # k máximo
    try:
        pistas(3, k=10)
        raise AssertionError("k=10 devia ser rejeitado")
    except ValueError:
        pass
    mo.callout(mo.md("`pistas` OK para $n=2$ e $n=3$."), kind="success")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    - **R5. Modelo CSP**
    """)
    return


@app.class_definition
class SudokuCSP:
    """Modelo CSP para uma grelha n² x n²."""

    def __init__(self, n):
        self.n = n
        self.N = n * n
        self.groups = []
        self._vizinhos = None

    def add_group(self, *grupos):
        """Adiciona um número arbitrário de grupos ao modelo."""
        for g in grupos:
            if not isinstance(g, Grupo):
                raise TypeError("O grupo tem de ser uma instância de Grupo")
            if g.n != self.n:
                raise ValueError("O grupo tem um n diferente do do modelo")
            self.groups.append(g)
        self._vizinhos = None          # a cache deixa de ser válida

    def _neighbors(self, cell):
        """Células que partilham algum grupo com `cell` (calculado uma só vez)."""
        if self._vizinhos is None:
            self._vizinhos = {}
            for g in self.groups:
                for c in g.cells:
                    self._vizinhos.setdefault(c, set()).update(g.cells)
            for c, viz in self._vizinhos.items():
                viz.discard(c)
        return self._vizinhos.get(cell, set())

    def _fixed_values(self):
        """valores fixados pelas pistas. None se a mesma célula tiver duas pistas diferentes"""
        fixed = {}
        for group in self.groups:
            for cell, value in group.cells.items():
                if value is not None:
                    if cell in fixed and fixed[cell] != value:
                        return None
                    fixed[cell] = value
        return fixed

    def _initial_domains(self):
        fixed = self._fixed_values()
        if fixed is None:
            return None
        valores = set(range(1, self.N + 1))
        return {(i, j): ({fixed[(i, j)]} if (i, j) in fixed else set(valores))
                for i in range(self.N) for j in range(self.N)}

    def _propagate(self, domains):
        """remove o valor de cada célula já decidida dos domínios dos vizinhos.
        Devolve False se dois vizinhos ficarem decididos com o mesmo valor."""
        changed = True
        while changed:
            changed = False
            for cell in domains:
                if len(domains[cell]) != 1:
                    continue
                value = next(iter(domains[cell]))
                for neighbor in self._neighbors(cell):
                    if len(domains[neighbor]) > 1 and value in domains[neighbor]:
                        domains[neighbor].remove(value)
                        changed = True
        #conflito: duas células decididas do mesmo grupo com o mesmo valor
        for group in self.groups:
            usados = set()
            for cell in group.cells:
                if len(domains[cell]) == 1:
                    value = next(iter(domains[cell]))
                    if value in usados:
                        return False
                    usados.add(value)
        return True

    def _select_cell(self, domains):
        """célula por decidir com menos valores possíveis"""
        candidates = [c for c in domains if len(domains[c]) > 1]
        if not candidates:
            return None
        return min(candidates, key=lambda c: len(domains[c]))

    def _backtrack(self, domains):
        if not self._propagate(domains):
            return None
        cell = self._select_cell(domains)
        if cell is None:
            return domains
        for value in sorted(domains[cell]):
            new_domains = {c: set(v) for c, v in domains.items()}
            new_domains[cell] = {value}
            result = self._backtrack(new_domains)
            if result is not None:
                return result
        return None

    def solve(self):
        """grelha preenchida (lista de listas) ou None se não houver solução."""
        domains = self._initial_domains()
        if domains is None:
            return None
        result = self._backtrack(domains)
        if result is None:
            return None
        return [[next(iter(result[(i, j)])) for j in range(self.N)]
                for i in range(self.N)]


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Teste R5**
    """)
    return


@app.cell
def _(mo):
    _modelo = SudokuCSP(3)

    _grupo = Grupo(3)

    _grupo.add(0, 0, 1)
    _grupo.add(0, 1, 2)
    _grupo.add(0, 2, 3)

    _modelo.add_group(_grupo)

    _solucao = _modelo.solve()

    assert _solucao is not None

    assert _solucao[0][0] == 1
    assert _solucao[0][1] == 2
    assert _solucao[0][2] == 3


    #n=2
    _modelo2 = SudokuCSP(2)

    _grupo2 = Grupo(2)

    _grupo2.add(0, 0, 1)
    _grupo2.add(0, 1, 2)

    _modelo2.add_group(_grupo2)

    _solucao2 = _modelo2.solve()

    assert _solucao2 is not None

    assert _solucao2[0][0] == 1
    assert _solucao2[0][1] == 2


    mo.callout(
        mo.md("`SudokuCSP` OK para $n=3$ e $n=2$."),
        kind="success"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **R6- Montar e resolver o Sudoku**: Cria e resolve um Sudoku n² x n² com pistas aleatórias
    """)
    return


@app.cell
def _(pistas):
    def sudoku(n, k=None):
        N = n * n

        #cria o modelo CSP
        modelo = SudokuCSP(n)

        #linhas
        for i in range(N):
            modelo.add_group(
                Path(n, (i, 0), (i, N - 1))
            )

        #colunas
        for j in range(N):
            modelo.add_group(
                Path(n, (0, j), (N - 1, j))
            )

        #blocos n x n
        for bi in range(n):
            for bj in range(n):
                modelo.add_group(
                    Cube(n, bi, bj)
                )

        #pistas aleatórias
        grupo_pistas = pistas(n, k)

        modelo.add_group(grupo_pistas)

        #resolve
        solucao = modelo.solve()

        return solucao, grupo_pistas

    return (sudoku,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Teste R6**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Validar automaticamente**
    """)
    return


@app.function
def validar(solucao, n, grupo_pistas):
    """Valida uma solução de Sudoku."""

    N = n * n
    esperado = set(range(1, N + 1))

    # Verificar dimensões
    assert len(solucao) == N
    assert all(len(linha) == N for linha in solucao)

    # Verificar valores
    assert all(
        valor in esperado
        for linha in solucao
        for valor in linha
    )

    # Verificar linhas
    for i in range(N):
        assert set(solucao[i]) == esperado

    # Verificar colunas
    for j in range(N):
        coluna = {
            solucao[i][j]
            for i in range(N)
        }

        assert coluna == esperado

    # Verificar blocos
    for bi in range(n):
        for bj in range(n):

            bloco = {
                solucao[bi * n + di][bj * n + dj]
                for di in range(n)
                for dj in range(n)
            }

            assert bloco == esperado

    # Verificar pistas
    for (i, j), valor in grupo_pistas.cells.items():
        if valor is not None:
            assert solucao[i][j] == valor

    return True


@app.cell
def _(mo, sudoku):
    for _n in (2, 3):
        _s, _p = sudoku(_n)
        assert _s is not None, f"n={_n}: puzzle sem solução com estas pistas"
        validar(_s, _n, _p)

    mo.callout(
        mo.md("Sudoku $4\\times4$ e $9\\times9$ resolvidos e validados com sucesso!"),
        kind="success",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Mostrar o sudoku**
    """)
    return


@app.cell
def _(mo):
    def mostrar_grelha(solucao, n, grupo_pistas):
        N = n * n
        pistas_pos = set(grupo_pistas.cells)
        linhas = []
        for i in range(N):
            celulas = []
            for j in range(N):
                estilo = "border:1px solid #999;width:2em;height:2em;text-align:center;"
                if j % n == 0:
                    estilo += "border-left:3px solid currentColor;"
                if i % n == 0:
                    estilo += "border-top:3px solid currentColor;"
                if j == N - 1:
                    estilo += "border-right:3px solid currentColor;"
                if i == N - 1:
                    estilo += "border-bottom:3px solid currentColor;"
                if (i, j) in pistas_pos:
                    estilo += "font-weight:bold;background:#ffe08a;color:#000;"
                celulas.append(f"<td style='{estilo}'>{solucao[i][j]}</td>")
            linhas.append("<tr>" + "".join(celulas) + "</tr>")
        return mo.Html("<table style='border-collapse:collapse'>" + "".join(linhas) + "</table>")

    return (mostrar_grelha,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Função que mostra o sudoku
    """)
    return


@app.cell
def _(mo, mostrar_grelha, sudoku):
    _s, _p = sudoku(3)
    mostrar_grelha(_s, 3, _p) if _s is not None else mo.md("Sem solução com estas pistas.")
    return


if __name__ == "__main__":
    app.run()
