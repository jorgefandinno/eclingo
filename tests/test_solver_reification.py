import unittest
import eclingo as _eclingo
from clingo.symbol import Function
from eclingo.solver.world_view import EpistemicLiteral, WorldView
from eclingo.solver import SolverReification

# python -m unittest tests.test_solver_reification.TestEclingoSolverReification.test_solver_reification01

""" SOLVER for test_solver """
def solve(reified_program):
        config = _eclingo.config.AppConfig()
        config.eclingo_semantics = "c19-1"
        
        solver = SolverReification(reified_program, config)
        
        wviews = []
        for model in solver.solve():
            if model not in wviews:
                wviews.append(model)
        return sorted(wviews)
            
class TestCase(unittest.TestCase):
    def assert_models(self, models, expected):
        self.assertEqual(models, expected)

class TestEclingoSolverReification(TestCase): 

    def test_solver_reification01(self):
        
        self.assert_models(solve("""tag(incremental). atom_tuple(0). atom_tuple(0,1). literal_tuple(0).
                                    rule(disjunction(0),normal(0)). atom_tuple(1).
                                    atom_tuple(1,2). rule(choice(1),normal(0)). atom_tuple(2).
                                    atom_tuple(2,3). literal_tuple(1). literal_tuple(1,2).
                                    rule(disjunction(2),normal(1)). output(k(u(a)),1).
                                    output(u(a),0). literal_tuple(2). literal_tuple(2,3). output(u(b),2)."""),
                            [
                               WorldView(
                                   [EpistemicLiteral(
                                       Function(
                                           'a', [], True), 0, False
                                       )
                                    ]
                                )
                            ]
                           )