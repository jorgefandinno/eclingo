import unittest
from eclingo.internal_states.internal_control import InternalStateControl
from eclingo.solver.tester import CandidateTesterReification
from clingo.symbol import Function
from eclingo.solver.generator import GeneratorReification
from eclingo.solver.world_view_builder import WorldWiewBuilderReification
import eclingo as _eclingo
from eclingo.solver.world_view import EpistemicLiteral, WorldView
from eclingo.literals import Literal
from clingo.ast import Sign

""" Helper function to generate candidates for a given program and test them"""
def world_view_builder(program):

        control = InternalStateControl(message_limit=0)
        control.configuration.solve.models = 0
        config = _eclingo.config.AppConfig()
        config.eclingo_semantics = "c19-1"
        
        control.add_program(program)
        control.ground([("base", [])])
        
        candidate_generator = GeneratorReification(config, control)
        
        candidates = list(candidate_generator())

        test_candidate = CandidateTesterReification(config, control)
        
        world_view_builder = WorldWiewBuilderReification(control)
        
        wviews = []
        for candidate in candidates:
            if test_candidate(candidate):
                wview = world_view_builder(candidate)
                if wview not in wviews:
                    wviews.append(wview)
                    print("World View of candidate generated: ", wview)
        
        return sorted(wviews)      
    
class TestCase(unittest.TestCase):
    maxDiff = None
    
    def assert_models(self, candidates, expected):
        self.assertEqual(candidates, expected)
        
    def test_wview_reification1(self):
        # echo ":- k(u(a)). u(a). {k(u(a))} :- u(a)." | clingo --output=reify
        self.assert_models(world_view_builder("""atom_tuple(0). atom_tuple(0,1). literal_tuple(0).
                                    rule(disjunction(0),normal(0)). atom_tuple(1).
                                    atom_tuple(1,2). rule(choice(1),normal(0)). atom_tuple(2).
                                    atom_tuple(2,3). literal_tuple(1). literal_tuple(1,2).
                                    rule(disjunction(2),normal(1)). output(k(u(a)),1).
                                    output(u(a),0). literal_tuple(2). literal_tuple(2,3). output(u(b),2)."""),
                           
                           [WorldView([EpistemicLiteral(Function('a', [], True), 0, False)])])
        
        
    def test_wview_reification2(self):
        # echo "a. b :- &k{ not not a }." | eclingo --output=reify --semantics c19-1
        self.assert_models(world_view_builder("""atom_tuple(0). atom_tuple(0,1). literal_tuple(0). rule(disjunction(0),normal(0)).
                                  atom_tuple(1). atom_tuple(1,2). rule(choice(1),normal(0)). atom_tuple(2). atom_tuple(2,3).
                                  literal_tuple(1). literal_tuple(1,2). rule(disjunction(2),normal(1)).output(k(not2(u(a))),1).
                                  output(u(a),0). literal_tuple(2). literal_tuple(2,3). output(u(b),2)."""),
                          
                           [WorldView([EpistemicLiteral(Literal(Function('a', [], True), Sign.DoubleNegation), 0, False)])])
        
    def test_wview_reification3(self):
        # echo "u(-a). u(b) :- k(u(-a)). u(c) :- k(u(b)). {k(u(-a))}. {k(u(b))}." | clingo --output=reify
        self.assert_models(world_view_builder("""atom_tuple(0). atom_tuple(0,1). literal_tuple(0). rule(disjunction(0),normal(0)).
                                  atom_tuple(1). atom_tuple(1,2). rule(choice(1),normal(0)). atom_tuple(2).
                                  atom_tuple(2,3). rule(choice(2),normal(0)). atom_tuple(3). atom_tuple(3,4). literal_tuple(1).
                                  literal_tuple(1,2). rule(disjunction(3),normal(1)). atom_tuple(4). atom_tuple(4,5).
                                  literal_tuple(2). literal_tuple(2,3). rule(disjunction(4),normal(2)). output(k(u(b)),1). 
                                  output(k(u(-a)),2). output(u(-a),0). literal_tuple(3). literal_tuple(3,4). 
                                  output(u(c),3). literal_tuple(4). literal_tuple(4,5). output(u(b),4)."""),
                           
                           [WorldView([EpistemicLiteral(Literal(Function('b', [], True), Sign.NoSign), 0, False),
                            EpistemicLiteral(Literal(Function('a', [], False), Sign.NoSign), 0, False)]),
                            WorldView([EpistemicLiteral(Literal(Function('a', [], False), Sign.NoSign), 0, False),
                            EpistemicLiteral(Literal(Function('b', [], True), Sign.NoSign), 0, False)])])
        
        