import unittest
from clingo.symbol import Function
from eclingo.solver.world_view_builder import WorldWiewBuilderReification
import eclingo as _eclingo
from eclingo.solver.world_view import EpistemicLiteral, WorldView
from eclingo.literals import Literal
from eclingo.solver.candidate import Candidate
from clingo.ast import Sign

# python -m unittest tests.test_worldview_builder_reification.TestEclingoWViewReification

""" Helper function to generate candidates for a given program and test them"""
def world_view_builder(tested_candidates):

        config = _eclingo.config.AppConfig()
        config.eclingo_semantics = "c19-1"
        
        world_view_builder = WorldWiewBuilderReification()
        
        wviews = []                     
        for candidate in tested_candidates:
            wview = world_view_builder(candidate)
            if wview not in wviews:
                wviews.append(wview)
                print("World View of candidate generated: ", wview)
        
        return sorted(wviews)      
    
class TestCase(unittest.TestCase):
    maxDiff = None
    
    def assert_models(self, candidates, expected):
        self.assertEqual(candidates, expected)
        
class TestEclingoWViewReification(TestCase):
    def test_wview_reification1(self):
        # echo ":- k(u(a)). u(a). {k(u(a))} :- u(a)." | clingo --output=reify
        # "a. b :- &k{a}."
        self.assert_models(world_view_builder(
                                [
                                    Candidate(
                                        pos=[
                                            Function(
                                                "k", [Function("u", [Function("a", [], True)], True)], True
                                            )
                                        ],
                                        neg=[],
                                    )
                                ]
                            ),
                           
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
        
        
        
    def test_wview_reification2(self):
        # echo "a. b :- &k{ not not a }." | eclingo --output=reify --semantics c19-1 --reification
        self.assert_models(world_view_builder(
                                            [
                                                Candidate(
                                                    pos=[],
                                                    neg=[
                                                        Function(
                                                            "k",
                                                            [
                                                                Function(
                                                                    "not2",
                                                                    [Function("u", [Function("a", [], True)], True)],
                                                                    True,
                                                                )
                                                            ],
                                                            True,
                                                        )
                                                    ],
                                                )
                                            ]
                                        ),
                          
                                        [
                                            WorldView(
                                                [EpistemicLiteral(
                                                    Literal(
                                                        Function('a', [], True), Sign.DoubleNegation), 0, False
                                                    )
                                                 ]
                                            )
                                        ]
                                    )
        
    def test_wview_reification3(self):
        # echo "-a. b:- &k{-a}. c :- b." | eclingo --semantics c19-1 --reification --output=reify
        self.assert_models(world_view_builder(
                            [
                                Candidate(
                                    pos=[
                                        Function(
                                            "k", [Function("u", [Function("a", [], False)], True)], True
                                        )
                                    ],
                                    neg=[],
                                )
                            ]
                            ),
                           
                            [
                                WorldView(
                                    [EpistemicLiteral(
                                        Literal(
                                            Function('a', [], False), Sign.NoSign), 0, False
                                        )
                                    ]
                                )
                                ]
                            )
        
    def test_wview_reification4(self):
        # echo "-a. b :- &k{-a}. c :- &k{b}." | eclingo --semantics c19-1 --reification
        self.assert_models(world_view_builder(
                            [
                            Candidate(
                                pos=[
                                    Function(
                                        "k", [Function("u", [Function("b", [], True)], True)], True
                                    ),
                                    Function(
                                        "k", [Function("u", [Function("a", [], False)], True)], True
                                    ),
                                ],
                                neg=[],
                            ),
                            ]
                            ),
                           
                            [
                                WorldView(
                                    [EpistemicLiteral(
                                        Function(
                                            'b', [], True), Sign.NoSign, False
                                        ), 
                                    EpistemicLiteral(
                                        Function(
                                            'a', [], False), 0, False
                                        )
                                    ]
                                    )
                                ]
                            )
        
    def test_wview_reification5(self):
        # echo "-a. b :- &k{-a}." | eclingo --semantics c19-1 --reification
        self.assert_models(world_view_builder(
                            [
                                Candidate(
                                    pos=[
                                        Function(
                                            "k", [Function("u", [Function("a", [], False)], True)], True
                                        )
                                    ],
                                    neg=[],
                                )
                            ]
                            ),
                            [
                               WorldView(
                                   [EpistemicLiteral(
                                       Function(
                                           'a', [], False), 0, False
                                       )
                                    ]
                                )
                            ]
                            )
        
    def test_wview_reification6(self):
        # echo "b :- &k{ not a }. c :- &k{ b }." | eclingo --semantics c19-1 --reification
        self.assert_models(world_view_builder(
            [
                                Candidate(
                                    pos=[
                                        Function(
                                        "k", [Function("u", [Function("b", [], True)], True)], True
                                        ),
                                        Function(
                                            "k", [Function("not1", [Function("u", [Function("a", [], True)], True)], True)]
                                        )
                    
                                    ],
                                    neg=[],
                                )
                            ]
        ),
                           [
                                WorldView(
                                    [EpistemicLiteral(
                                        Literal(
                                            Function('a', [], True), Sign.Negation), 0, False
                                        ), 
                                    EpistemicLiteral(
                                        Literal(
                                            Function('b', [], True), Sign.NoSign), 0, False
                                        )
                                    ]
                                    )
                                ]
        )
            
        
        