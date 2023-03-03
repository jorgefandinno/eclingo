import unittest
from eclingo.internal_states.internal_control import InternalStateControl
from eclingo.solver.candidate import Candidate
from eclingo.solver.tester import CandidateTesterReification
from clingo.symbol import Function
from eclingo.solver.generator import GeneratorReification
import eclingo as _eclingo

# Input Tests
# echo ":- &k{a}. a." | eclingo --output=reify --reification --semantics c19-1
# echo ":- k(u(a)). u(a). {k(u(a))} :- u(a)." | clingo --output=reify
# echo "a. b :- &k{a}." | eclingo  --semantics c19-1 --reification
# echo "a. b :- &k{a}. {a}." | eclingo  --semantics c19-1 --reification -> Generator test equivalence

""" Helper function to generate candidates for a given program and test them"""
def tester(program):

        control = InternalStateControl(message_limit=0)
        control.configuration.solve.models = 0
        config = _eclingo.config.AppConfig()
        config.eclingo_semantics = "c19-1"
        
        control.add_program(program)
        control.ground([("base", [])])
        
        candidate_generator = GeneratorReification(config, control)
        
        candidates = list(candidate_generator())

        test_candidate = CandidateTesterReification(config, control)
        tested = []
        for candidate in candidates:
            if test_candidate(candidate):
                tested.append(candidate)
                # print("Candidate on tester generator: ", candidate)
        
        # print(sorted(tested))
        return sorted(tested)      
        
class TestCase(unittest.TestCase):
    def assert_models(self, candidates, expected):
        self.assertEqual(candidates, expected)
        
class TestEclingoTesterrReification(TestCase): 
    
    def test_tester_reification(self):
        # echo ":- k(u(a)). u(a). {k(u(a))} :- u(a)." | clingo --output=reify
        self.assert_models(tester("""atom_tuple(0). atom_tuple(0,1). literal_tuple(0).
                                    rule(disjunction(0),normal(0)). atom_tuple(1).
                                    atom_tuple(1,2). rule(choice(1),normal(0)). atom_tuple(2).
                                    atom_tuple(2,3). literal_tuple(1). literal_tuple(1,2).
                                    rule(disjunction(2),normal(1)). output(k(u(a)),1).
                                    output(u(a),0). literal_tuple(2). literal_tuple(2,3). output(u(b),2)."""),
                           
                           [Candidate(pos=[], neg=[Function('k', [Function('u', [Function('a', [], True)], True)], True)]),
                            Candidate(pos=[Function('k', [Function('u', [Function('a', [], True)], True)], True)], neg=[])])
        
        self.assert_models(tester("""atom_tuple(0). atom_tuple(0,1). literal_tuple(0). rule(choice(0),normal(0)).
                                    atom_tuple(1). atom_tuple(1,2). literal_tuple(1). literal_tuple(1,1). 
                                    rule(choice(1),normal(1)). atom_tuple(2). atom_tuple(2,3). literal_tuple(2). 
                                    literal_tuple(2,2). rule(disjunction(2),normal(2)). atom_tuple(3). literal_tuple(3). 
                                    literal_tuple(3,-1). rule(disjunction(3),normal(3)). output(u(a),1). literal_tuple(4). 
                                    literal_tuple(4,3). output(u(b),4). output(k(u(a)),2)."""),
                           
                           [Candidate(pos=[], neg=[Function('k', [Function('u', [Function('a', [], True)], True)], True)]),
                            Candidate(pos=[Function('k', [Function('u', [Function('a', [], True)], True)], True)], neg=[])])

    def test_tester_reification_negation(self):
            # echo "{u(a)}. :- not1(u(a)). u(b) :- k(u(a)). {k(u(a))}. {not1(u(a))}." | clingo --output=reify
        self.assert_models(tester("""atom_tuple(0). atom_tuple(0,1). literal_tuple(0). rule(choice(0),normal(0)).
                                  atom_tuple(1). atom_tuple(1,2). rule(choice(1),normal(0)). atom_tuple(2). 
                                  atom_tuple(2,3). literal_tuple(1). literal_tuple(1,2). rule(disjunction(2),normal(1)). 
                                  atom_tuple(3). literal_tuple(2). literal_tuple(2,1). rule(disjunction(3),normal(2)). 
                                  atom_tuple(4). atom_tuple(4,4). rule(choice(4),normal(0)). literal_tuple(3). 
                                  literal_tuple(3,3). output(u(b),3). literal_tuple(4). literal_tuple(4,4). 
                                  output(u(a),4). output(not1(u(a)),2). output(k(u(a)),1)."""),
                          
                           [Candidate(pos=[], neg=[Function('k', [Function('u', [Function('a', [], True)], True)], True)]),
                            Candidate(pos=[], neg=[Function('k', [Function('u', [Function('a', [], True)], True)], True)]),
                            Candidate(pos=[Function('k', [Function('u', [Function('a', [], True)], True)], True)], neg=[]),
                             Candidate(pos=[Function('k', [Function('u', [Function('a', [], True)], True)], True)], neg=[])])
        
    def test_tester_reification_double_negation(self):
        # echo "a. b :- &k{ not not a }." | eclingo --output=reify --semantics c19-1
        self.assert_models(tester("""atom_tuple(0). atom_tuple(0,1). literal_tuple(0). rule(disjunction(0),normal(0)).
                                  atom_tuple(1). atom_tuple(1,2). rule(choice(1),normal(0)). atom_tuple(2). atom_tuple(2,3).
                                  literal_tuple(1). literal_tuple(1,2). rule(disjunction(2),normal(1)).output(k(not2(u(a))),1).
                                  output(u(a),0). literal_tuple(2). literal_tuple(2,3). output(u(b),2)."""),
                          
                           [Candidate(pos=[], neg=[Function('k', [Function('not2' , [Function('u', [Function('a', [], True)], True)], True)], True)]),
                           Candidate(pos=[Function('k', [Function('not2', [Function('u', [Function('a', [], True)], True)], True)], True)], neg=[])])
    
    def test_tester_reification_explicit_negation(self):
        # echo "u(-a). u(b) :- k(u(-a)). u(c) :- k(u(b)). {k(u(-a))}. {k(u(b))}." | clingo --output=reify
        self.assert_models(tester("""atom_tuple(0). atom_tuple(0,1). literal_tuple(0). rule(disjunction(0),normal(0)).
                                  atom_tuple(1). atom_tuple(1,2). rule(choice(1),normal(0)). atom_tuple(2).
                                  atom_tuple(2,3). rule(choice(2),normal(0)). atom_tuple(3). atom_tuple(3,4). literal_tuple(1).
                                  literal_tuple(1,2). rule(disjunction(3),normal(1)). atom_tuple(4). atom_tuple(4,5).
                                  literal_tuple(2). literal_tuple(2,3). rule(disjunction(4),normal(2)). output(k(u(b)),1). 
                                  output(k(u(-a)),2). output(u(-a),0). literal_tuple(3). literal_tuple(3,4). 
                                  output(u(c),3). literal_tuple(4). literal_tuple(4,5). output(u(b),4)."""),
                           
                           [Candidate(pos=[], neg=[Function('k', [Function('u', [Function('b', [], True)], True)], True),
                                                   Function('k', [Function('u', [Function('a', [], False)], True)], True)]),
                            Candidate(pos=[Function('k', [Function('u', [Function('b', [], True)], True)], True)],
                                      neg=[Function('k', [Function('u', [Function('a', [], False)], True)], True)]),
                            Candidate(pos=[Function('k', [Function('u', [Function('b', [], True)], True)], True),
                                           Function('k', [Function('u', [Function('a', [], False)], True)], True)], neg=[]),
                            Candidate(pos=[Function('k', [Function('u', [Function('a', [], False)], True)], True)],
                                      neg=[Function('k', [Function('u', [Function('b', [], True)], True)], True)])])
        
        # echo "u(-a). u(b) :- k(u(-a)). u(c) :- k(u(b))." | clingo --output=reify
        self.assert_models(tester("""atom_tuple(0). atom_tuple(0,1). literal_tuple(0). rule(disjunction(0),normal(0)). 
                                  atom_tuple(1). atom_tuple(1,2). rule(choice(1),normal(0)). atom_tuple(2).
                                  atom_tuple(2,3). literal_tuple(1). literal_tuple(1,2). rule(disjunction(2),normal(1)). 
                                  output(k(u(-a)),1). output(u(-a),0). literal_tuple(2). literal_tuple(2,3). output(u(b),2)."""),
                           
                           [Candidate(pos=[], neg=[Function('k', [Function('u', [Function('a', [], False)], True)], True)]),
                            Candidate(pos=[Function('k', [Function('u', [Function('a', [], False)], True)], True)], neg=[])])
                      
