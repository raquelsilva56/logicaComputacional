from z3 import * 
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
            t['y'] == LShr(s['y'],1), #div por 2 sem sinal
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