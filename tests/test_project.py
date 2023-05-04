import unittest
import eclingo as _eclingo
from clingo.symbol import Function
from eclingo.solver.world_view import EpistemicLiteral, WorldView
from eclingo.literals import Literal
from eclingo.solver import SolverReification
from eclingo.internal_states import internal_control
from clingo.ast import Sign

# python -m unittest tests.test_project.TestEclingoProject.test_project0

def project(reified_program):
        config = _eclingo.config.AppConfig()
        config.eclingo_semantics = "c19-1"
        
        # We have no way of testing this, unless we make that parameter part of the configuration.
        config.control.configuration.solve.project = "auto,3"
        
        # control = internal_control.InternalStateControl(["0"], message_limit=0)
        # control.configuration.solve.project = "auto,3"
        
        solver = SolverReification(reified_program, config)
        
        wviews = []
        for model in solver.solve():
            #if model not in wviews: 
            # This line obviously solves the problem, but just because does not append equals
            wviews.append(model)
        return sorted(wviews)


class TestCase(unittest.TestCase):
    def assert_models(self, models, expected):
        self.assertEqual(models, expected)


class TestEclingoProject(TestCase): 
    
    # Given auto,3 should not give 2 world views.
    def test_project0(self):
        self.maxDiff = None
        #echo "b :- &k{ not a }. c :- &k{ b }. {a}." | eclingo --semantics c19-1 --reification
        self.assert_models(project("""tag(incremental). atom_tuple(0). atom_tuple(0,1). literal_tuple(0).
                                   rule(choice(0),normal(0)). atom_tuple(1). atom_tuple(1,2). literal_tuple(1). 
                                   literal_tuple(1,-1). rule(disjunction(1),normal(1)). atom_tuple(2). atom_tuple(2,3). literal_tuple(2). 
                                   literal_tuple(2,2). rule(choice(2),normal(2)). atom_tuple(3). atom_tuple(3,4). literal_tuple(3). 
                                   literal_tuple(3,3). rule(disjunction(3),normal(3)). output(k(not1(u(b))),3). literal_tuple(4). 
                                   literal_tuple(4,1). output(u(b),4). literal_tuple(5). literal_tuple(5,4). output(u(a),5). 
                                   output(not1(u(b)),2). rule(choice(0),normal(0)). rule(disjunction(1),normal(1)).
                                   rule(choice(2),normal(2)). rule(disjunction(3),normal(3))."""),
                           [
                                WorldView(
                                    [
                                        EpistemicLiteral(
                                            Literal(Function("b", [], True), Sign.NoSign), 0, True
                                        )
                                    ]
                                ),
                                WorldView(
                                    [
                                        EpistemicLiteral(
                                            Literal(Function("b", [], True), Sign.NoSign), 0, True
                                        )
                                    ]
                                )
                            ]
        )
