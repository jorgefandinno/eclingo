import unittest
from eclingo.internal_states.internal_control import InternalStateControl
from eclingo.solver.candidate import Candidate
from clingo.symbol import Function
from eclingo.solver.generator import GeneratorReification
from eclingo.config import AppConfig
import eclingo as _eclingo


""" Helper function to generate candidates for a given program """
def generate(program):

        control = InternalStateControl(message_limit=0)
        control.configuration.solve.models = 0
        config = _eclingo.config.AppConfig()
        config.eclingo_semantics = "c19-1"
        
        control.add_program(program)
        control.ground([("base", [])])
        
        candidate_generator = GeneratorReification(config, control)
        
        candidates = list(candidate_generator())
        for candidate in candidates:
            print("HERE " + str(candidate))
        
        return sorted(candidates)
            
            
class TestCase(unittest.TestCase):
    def assert_models(self, models, expected):
        self.assertEqual(str(models), expected)

class TestEclingoGenerator(TestCase): 

    def test_generator01(self):
        self.assert_models(generate("""atom_tuple(0). atom_tuple(0,1). literal_tuple(0).
                                    rule(disjunction(0),normal(0)). atom_tuple(1).
                                    atom_tuple(1,2). rule(choice(1),normal(0)). atom_tuple(2).
                                    atom_tuple(2,3). literal_tuple(1). literal_tuple(1,2).
                                    rule(disjunction(2),normal(1)). output(k(u(a)),1).
                                    output(u(a),0). literal_tuple(2). literal_tuple(2,3). output(u(b),2)."""),
                           [Candidate(pos=[], neg=[Function('k_u_a', [], True)]), Candidate(pos=[Function('k_u_a', [], True)], neg=[])])        