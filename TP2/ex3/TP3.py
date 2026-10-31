from z3 import BitVec, And, Or, ULT, UGE, LShR, Solver, sat, unsat, Not
#tenho de usar ULT por causa do aviso do PDF sem sinal. 
#overflow no left skip do pdf


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
               ULT(s['z'] + s['x'], s['z']),   # verflow na soma
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
def trans(s,t):
    return Or(init_skip(s,t), skip_left(s,t), skip_stop(s,t), left_skip(s,t), left_error(s,t), skip_right(s,t), right_skip(s,t), right_error(s,t))

#teste p ver se o automato multiplica mm. Pedi ao z3 um percurso q comece com a=3, b=2, e acabe em stop com z==6
def teste1():
    K=6 #numero de passos
    st= [declare(i) for i in range(K+1)]
    sol=Solver()
    sol.add(init(st[0]),st[0]['a']==3, st[0]['b']==2)
    for i in range(K):
        sol.add(trans(st[i], st[i+1]))
    sol.add(Or([And(s['pc']==5, s['z']==6)for s in st]))
    print(sol.check()) #tem de imprimir sat, tem 6 passos (init → skip → left → skip → right → skip → stop)

teste1()


#parte b) k-inducao, provar que P(s) := x*y + z == a*b vale em todos os estados alcancaveis.
# nao da para percorrer tudo(infinitos) logo a inducao usa duas verificacoes: Para k=1:
#Base: estado inicial cumpre P. Inducao: se um estado cumpre P e vai para outro, esse tbm cumpre P.
#Em ambas, decidi pedir um contra-exemplo ao z3, unsat se nao houver, logo esta provado. 

def P(s):
    return s['x']*s['y'] + s['z'] == s['a']*s['b'] #formula a provar

"""def base():
    s0= declare(0)
    sol=Solver()
    sol.add(init(s0), Not(P(s0))) #procura contraexemplo, por isso o uso de NOT
    print("base:",sol.check()) #tem de imprimir unsat

def inducao():
    s0= declare(0)
    s1= declare(1)
    sol=Solver()
    sol.add(P(s0), trans(s0,s1), Not(P(s1)))#P agora, e o proximo falha?
    r=sol.check()
    print("inducao:",r) #unsat tambem 
    if r==sat:
        print(sol.model()) #mostra o contra-exemplo"""



#com k=1 nao deu certo, pois nao pode acontecer y impar e estar no left, logo temos de subir k 
#para k=2
#pedir ao claude para juntar  

def K(k):
    st = [declare(i) for i in range(k + 1)]

    #base: P no estado inicial
    sol = Solver()
    sol.add(init(st[0]))
    for i in range(k - 1):
        sol.add(trans(st[i], st[i + 1]))
    sol.add(Or([Not(P(st[i])) for i in range(k)]))
    print("base:", sol.check()) #unsat

    #inducao: P em k estados seguidos
    sol = Solver()
    for i in range(k):
        sol.add(P(st[i]), trans(st[i], st[i + 1]))
    sol.add(Not(P(st[k])))
    print("inducaoK:", sol.check())  #unsat 

K(1)
K(2)
