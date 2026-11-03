import unittest
from z3 import And, sat, unsat
from TP3 import (declare, init, trans, erro, caminho, P, init_c, Q,
                  induction_always, Kinduction_always, decresce_forall, v_zero)


#testes gerados com ajuda de LLM

class TestModelo(unittest.TestCase): #testa a)
    def test_3_vezes_2(self):
        ini=lambda s: And(init(s), s['a']==3, s['b']==2)
        self.assertEqual(caminho(6,ini,lambda s: And(s['pc']==5, s['z']==6)), sat) #3*2=6

    def test_3_vezes_2_resultado_errado(self):
        ini = lambda s: And(init(s), s['a'] == 3, s['b'] == 2)
        self.assertEqual(caminho(6, ini, lambda s: And(s['pc'] == 5, s['z'] != 6)), unsat)

    def test_overflow(self):
        ini = lambda s: And(init(s), s['a'] == 200, s['b'] == 2)
        self.assertEqual(caminho(3, ini, erro), sat)



class TestInvariante(unittest.TestCase): #testa b)
    #a prova do k2 é mais lenta que as outras porque o Z3 tem de raciocinar
    #sobre multiplicações de bits, e isso mostra que a escolha de n influencia o custo da verificação.
    def test_k1_nao_basta(self):
        self.assertEqual(induction_always(declare, init,trans,P),"Passo Indutivo falha")

    def test_k2_prova(self):
        self.assertEqual(Kinduction_always(declare,init,trans,P,2),"invariante")



class TestSeguranca(unittest.TestCase): #testa c)
    def test_k1_nao_basta(self):
        self.assertEqual(Kinduction_always(declare,init_c,trans,Q,1),"Passo Indutivo falha")

    def test_k2_prova(self):
        self.assertEqual(Kinduction_always(declare,init_c,trans,Q,2),"invariante")



class testTermina(unittest.TestCase): #testa d)
    def test_decresce(self):
        self.assertEqual(Kinduction_always(declare,init,trans,decresce_forall,1),"invariante")

    def test_v_zero(self):
        self.assertEqual(Kinduction_always(declare,init,trans,v_zero,1),"invariante")