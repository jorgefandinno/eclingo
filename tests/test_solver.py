import unittest
import eclingo as _eclingo
from eclingo.internal_states.internal_control import InternalStateControl
from eclingo.control import Control
from eclingo.solver.generator import CandidateGenerator
from eclingo.solver import Solver


""" SOLVER for test_solver """
def solve(program):
        control = InternalStateControl(message_limit=0)
        config = _eclingo.config.AppConfig()
        config.eclingo_semantics = "c19-1"
        
        # Registering the eclingo control
        econtrol = Control(control=control, config=config)
        
        # Create the Candidate generator
        generate_candidate = CandidateGenerator(config, control)

        # Add control
        econtrol.add_program(program)
        print("Program: " + program)
        
        # World view list for generated candidates
        world_views = []
        
        # world_views = []
        for world_view in econtrol.solve():
            world_view = sorted(str(symbol) for symbol in world_view.symbols)
            world_views.append(world_view)
            print(sorted(world_views))
        return sorted(world_views)


        
# TODO: Write a test solver that once the flag eclingo-reification is passed,
# sets it to true, and uses reified terms as input for solver.
            
class TestCase(unittest.TestCase):
    def assert_models(self, models, expected):
        self.assertEqual(models, sorted(sorted(wv) for wv in expected))

class TestEclingoSolver(TestCase): 

    def test_positive_programs_solver(self):
        self.assert_models(solve("a. b :- &k{a}."), [["&k{a}"]])
        # self.assert_models(solve("{a}. :- not a. b :- &k{a}."), [["&k{a}"]])