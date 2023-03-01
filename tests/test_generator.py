import unittest
from eclingo.internal_states.internal_control import InternalStateControl
from eclingo.control import Control
from eclingo.config import AppConfig
import eclingo as _eclingo


class CandidateGeneratorTest(Control):
    
    def generator_solve(self):
        self.prepare_solver()

        candidates = []
        for candidate in self.solver.generate_candidates():
            candidates.append(candidate)
        return candidates


""" Helper function to generate candidates for a given program """
def generate(program):

        # Initialize 
        control = InternalStateControl(message_limit=0)
        config = _eclingo.config.AppConfig()
        config.eclingo_semantics = "c19-1"
        
        # Create Subclass of Control
        gener = CandidateGeneratorTest(control, config)
        gener.add_program(program)
        
        # Generate Candidates
        candidates = []
        candidates = gener.generator_solve()
        
        # print("All candidates for that: " + str(sorted(candidates)))
        return sorted(candidates)
            
            
class TestCase(unittest.TestCase):
    def assert_models(self, models, expected):
        self.assertEqual(str(models), expected)

class TestEclingoGenerator(TestCase): 

    def test_generator01(self):
        self.assert_models(generate("a. b :- &k{a}."), "[Candidate(pos=[Function('k_u_a', [], True)], neg=[])]")
        self.assert_models(generate("{a}. :- not a. b :- &k{a}."), "[Candidate(pos=[], neg=[Function('k_u_a', [], True)]), Candidate(pos=[Function('k_u_a', [], True)], neg=[])]")
        
    def test_generator02(self):
        self.assert_models(generate("a. b :- &k{a}. c :- &k{b}."), "[Candidate(pos=[Function('k_u_a', [], True)], neg=[Function('k_u_b', [], True)]), Candidate(pos=[Function('k_u_a', [], True), Function('k_u_b', [], True)], neg=[])]")