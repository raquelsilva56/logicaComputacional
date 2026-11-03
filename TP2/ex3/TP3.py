from z3 import BitVec, BitVecVal, And, Or, Not, If, Implies, ForAll, ULT, UGE, LShR, ZeroExt, Solver, sat, unsat
import unittest

n = 8 #tamanho dos bitvecs. Parametro

def declare(i): #declara estado s, declaro(0) da atual e o 1 o seguinte
    s={} 
    s['pc'] = BitVec('pc' + str(i), n) #program counter, em que nodo se esta
    s['a'] = BitVec('a' + str(i), n) #a e b n mudam durante a execucao mas defino agora
    s['b'] = BitVec('b' + str(i), n)
    s['x'] = BitVec('x' + str(i), n)
    s['y'] = BitVec('y' + str(i), n)
    s['z'] = BitVec('z' + str(i), n)
    return s

#diz o que acontece ao nodo pc,x,y,z. tipo init(x,y,z <- a,b,0) atribui ab0 a xyz

def init(s): #estado inicial, a e b livres ainda
    return And(s['pc'] == 0, s['x'] == s['a'], s['y'] == s['b'], s['z'] ==0)


#funcao de estado de transicao
#cada transicao e uma funcao (s,t) s=atual, t=seguinte.
def keep(s, t, nomes):
    return And([t[v] == s[v] for v in nomes])

#skip - left(y != 0 and even(y)), skip nao altera nadaa, so decide para onde ir
def skip_left(s,t):
    return And(s['pc'] == 1, s['y'] !=0, (s['y'] & 1)==0,
    t['pc'] ==2,
    keep(s,t, ['a','b','x','y','z']))

#skip-stop(y=0)
def skip_stop(s,t):
    return And(s['pc'] == 1, s['y']==0,
            t['pc'] == 5, 
            keep(s,t,['a','b','x','y','z']))

#left-skip (aplica x,y,z <- 2*x, y/2, z, se n houver overflow)

def left_skip(s,t):
    return And(s['pc'] == 2, 
            ULT(s['x'], 2**(n-1)), #sem overflow no shift
            t['pc'] ==1 ,
            t['x'] == s['x'] << 1,
            t['y'] == LShR(s['y'],1), #div por 2 sem sinal
            keep(s,t,['a', 'b' , 'z']))

#left- error(overflow), implementa a parte do pdf onde o erro tem precedencia: se ha overflow, so o ramo de erro e possivel
def left_error(s,t):
    return And(s['pc'] ==2,
    UGE(s['x'], 2**(n-1)), #ha overflow
    t['pc'] == 4, 
    keep(s,t,['a','b','x','y','z']))

#os padroes do right, muda a detecao do overflow

def right_skip(s, t):
    return And(s['pc'] == 3,
               UGE(s['z'] + s['x'], s['z']),   #sem overflow na soma
               t['pc'] == 1,
               t['y'] == s['y'] - 1,
               t['z'] == s['z'] + s['x'],
               keep(s, t, ['a','b','x']))

def right_error(s, t):
    return And(s['pc'] == 3,
               ULT(s['z'] + s['x'], s['z']),   # overflow na soma
               t['pc'] == 4,
               keep(s, t, ['a','b','x','y','z']))

#estado do erro tem de estar no nodo error
def erro(s):
    return s['pc'] == 4

def init_skip(s,t):
    return And(s['pc'] == 0, t['pc'] == 1,
            keep(s, t, ['a','b','x','y','z']))

#mesma coisa do skipleft mas com a condicao de y impar, vai para o nodo 3
def skip_right(s,t):
    return And(s['pc'] == 1, s['y'] != 0, (s['y'] & 1) == 1,
            t['pc'] == 3,
            keep(s, t, ['a','b','x','y','z']))

#tem 8 ramos, um por cada transicao possivel, retorna a disjuncao de todos os ramos possiveis
def ramos(s,t):
    return Or(init_skip(s,t), skip_left(s,t), skip_stop(s,t), left_skip(s,t), left_error(s,t), skip_right(s,t), right_skip(s,t), right_error(s,t))

def terminal(s): 
    return Or(s['pc'] == 4, s['pc'] == 5) #estado de erro ou stop

def laco(s,t):
    return And(terminal(s), keep(s,t,['pc','a','b','x','y','z']))
def trans(s,t):
    return Or(ramos(s,t),laco(s,t))


def induction_always(declare, init,trans,inv):
    #da ficha8
    s,t=declare(0), declare(1)
    sol=Solver()
    sol.add(init(s),Not(inv(s)))
    if sol.check() == sat: 
        return "Base falha"
    sol= Solver()
    sol.add(inv(s), trans(s,t),Not(inv(t)))
    if sol.check() == sat:
        return "Passo Indutivo falha"
    return "invariante"



def Kinduction_always(declare, init,trans, inv,k):
    st=[declare(i) for i in range(k+1)]
    sol=Solver()
    sol.add(init(st[0]))
    for i in range (k-1):
        sol.add(trans(st[i],st[i+1]))
    sol.add(Or([Not(inv(st[i]))for i in range(k)]))
    if sol.check()== sat:
        return "Base falha"
    sol=Solver()
    for i in range(k):
        sol.add(inv(st[i]), trans(st[i],st[i+1]))
    sol.add(Not(inv(st[k])))
    if sol.check() == sat:
        return "Passo Indutivo falha"
    return "invariante"


#parte b) k-inducao, provar que P(s) := x*y + z == a*b vale em todos os estados alcancaveis.
# nao da para percorrer tudo(infinitos) logo a inducao usa duas verificacoes: Para k=1:
#Base: estado inicial cumpre P. Inducao: se um estado cumpre P e vai para outro, esse tbm cumpre P.
#Em ambas, decidi pedir um contra-exemplo ao z3, unsat se nao houver, logo esta provado. 

def P(s):
    return s['x']*s['y'] + s['z'] == s['a']*s['b'] #formula a provar



#alinea c) Segurança, mostrar que, com a < 2^(n/2) e b < 2^(n/2), o estado de erro (pc == 4) nunca é acessível.

def init_c(s):
    return And(init(s), ULT(s['a'], 2**(n//2)), ULT(s['b'], 2**(n//2)))

def W(v): #aumenta v em n para 2n bits
    return ZeroExt(n, v)

def Q(s):
    return And(Not(erro(s)),                                   #n esta no estado de erro
               ULT(s['a'], 2**(n//2)), ULT(s['b'], 2**(n//2)), # a e b pequenos
               W(s['x'])*W(s['y']) + W(s['z']) == W(s['a'])*W(s['b']))  #fomula a provar


#alinea d) variante. "o programa termina, quaisquer que sejam a e b", provar no SFOTS 

def caminho(K, inicio, final=None):
    #existe caminho com k transicoes a partir de 'inicio'?
    st=[declare(i) for i in range(K+1)]
    sol=Solver()
    sol.add(inicio(st[0]))
    for i in range(K):
        sol.add(trans(st[i],st[i+1]))
    if final:
        sol.add(final(st[K]))
    return sol.check() 

#propriedade de terminação(animação): F(G terminal)
#a partir de qualquer estado inicial (a,b,quaisquer), o sistema chega a um estado final
#(pc=4 ou =5) e assim fica(o laço garante a permanencia).
#Segui o método da ficha 8 onde a variante V tem 3 condições
#1) V>=0(auto: BitVecs s/sinal)
#2) V decresce estritam/ ou chega a 0 -> decresce_forall
#3) V=0 -> terminal -> v_zero


def V(s): #variante em 2n bits
    y=W(s['y'])
    w=If(s['pc']==0, BitVecVal(3,2*n),
         If(s['pc']==1, BitVecVal(2,2*n), BitVecVal(1,2*n)))
    return If(terminal(s), BitVecVal(0,2*n), 4*y+w)

def decresce(s,t): #V' <V ou V'=0 
    return Or(ULT(V(t),V(s)),V(t)==0)

def decresce_forall(s): #condiçao 2 da ficha com o "para todo"
    t=declare('p')
    return ForAll([t[v] for v in t], Implies(trans(s,t), decresce(s,t)))

def v_zero(s):
    return Implies(V(s)==0,terminal(s))

