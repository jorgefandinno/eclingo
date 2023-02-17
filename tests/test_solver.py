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

        # Add control
        econtrol.add_program(program)
    
        # World view list for generated candidates
        world_views = []
        
        for world_view in econtrol.solve():
            world_view = sorted(str(symbol) for symbol in world_view.symbols)
            world_views.append(world_view)
        return sorted(world_views)
            
class TestCase(unittest.TestCase):
    def assert_models(self, models, expected):
        self.assertEqual(models, sorted(sorted(wv) for wv in expected))

class TestEclingoSolver(TestCase): 

    def test_positive_programs_solver(self):
        self.assert_models(solve("a. b :- &k{a}."), [["&k{a}"]])
        self.assert_models(solve("{a}. :- not a. b :- &k{a}."), [["&k{a}"]])