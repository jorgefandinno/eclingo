import unittest
from eclingo.internal_states.internal_control import InternalStateControl
from eclingo.solver.candidate import Candidate
from eclingo.solver.tester import CandidateTesterReification
from clingo.symbol import Function
from eclingo.solver.generator import GeneratorReification
import eclingo as _eclingo


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
                print("On gen tester", candidate)
        
        return sorted(tested)      
        
class TestCase(unittest.TestCase):
    def assert_models(self, candidates, expected):
        self.assertEqual(candidates, expected)
        
class TestEclingoTesterrReification(TestCase): 
    # echo ":- k(u(a)). u(a). {k(u(a))} :- u(a)." | clingo --output=reify
    def test_tester01_reification(self):
        self.assert_models(tester("""atom_tuple(0). atom_tuple(0,1). literal_tuple(0).
                                    rule(disjunction(0),normal(0)). atom_tuple(1).
                                    atom_tuple(1,2). rule(choice(1),normal(0)). atom_tuple(2).
                                    atom_tuple(2,3). literal_tuple(1). literal_tuple(1,2).
                                    rule(disjunction(2),normal(1)). output(k(u(a)),1).
                                    output(u(a),0). literal_tuple(2). literal_tuple(2,3). output(u(b),2)."""),
                           
                           [Candidate(pos=[], neg=[Function('k', [Function('u', [Function('a', [], True)], True)], True)]),
                            Candidate(pos=[Function('k', [Function('u', [Function('a', [], True)], True)], True)], neg=[])])
        
        # self.assert_models(tester("""atom_tuple(0). atom_tuple(0,1). literal_tuple(0). rule(choice(0),normal(0)).
        #                             atom_tuple(1). atom_tuple(1,2). literal_tuple(1). literal_tuple(1,1). 
        #                             rule(choice(1),normal(1)). atom_tuple(2). atom_tuple(2,3). literal_tuple(2). 
        #                             literal_tuple(2,2). rule(disjunction(2),normal(2)). atom_tuple(3). literal_tuple(3). 
        #                             literal_tuple(3,-1). rule(disjunction(3),normal(3)). output(u(a),1). literal_tuple(4). 
        #                             literal_tuple(4,3). output(u(b),4). output(k(u(a)),2)."""),
                           
        #                    [Candidate(pos=[], neg=[Function('k', [Function('u', [Function('a', [], True)], True)], True)]),
        #                     Candidate(pos=[Function('k', [Function('u', [Function('a', [], True)], True)], True)], neg=[])])
