import unittest
import clingo
from clingo import Function, Number
from clingo import ast as _ast

from eclingo.util.groundprogram import *
import eclingo.internal_states.internal_control as internal_control

from clingo.ast import  parse_string, Location, Position

class Test(unittest.TestCase):

    def setUp(self):
        self.control = internal_control.InternalStateControl()

    def assert_models(self, models, obtained_models):
        models.sort()
        for model in obtained_models:
            model.sort()
        obtained_models = [' '.join(str(symbol) for symbol in model) for model in obtained_models]
        obtained_models.sort()
        self.assertEqual(obtained_models, models)


    def test_prg01(self):
        """Checks that the models of program are models.
        Only two are obtained and this depends on the random seed.
        New versions of clingo may break it.
        """
        program = """
        {a}.
        {b}.
        c :- a.
        #project c.
        """
        models = ['a c', '']
        
        self.control.configuration.solve.project = "auto,3"
        self.control.configuration.solve.models  = 0

        self.control.add("base", [], program)
        self.control.ground([("base", [])])
        with self.control.solve(yield_=True) as handle:
            obtained_models = [list(model.symbols(shown=True)) for model in handle]
        self.assert_models(models, obtained_models)
    

    def test_prg01_pretty_ground_program(self):
        program = """
        {a}.
        {b}.
        c :- a.
        #project c.
        """

        self.control.configuration.solve.project = "auto,3"
        self.control.configuration.solve.models  = 0

        self.control.add("base", [], program)
        self.control.ground([("base", [])])
        self.assertEqual(sorted(str(self.control.ground_program).replace(' ','').replace('\n','').split('.')), sorted(program.replace(' ','').replace('\n','').split('.')))




    def test_prg01_pretty_ground_program_add(self):
        program = """
        {a}.
        {b}.
        c :- a.
        #project c.
        """      
        
        self.control.configuration.solve.project = "auto,3"
        self.control.configuration.solve.models  = 0

        self.control.add("base", [], program)
        self.control.ground([("base", [])])
        with self.control.backend() as backend:
            backend.add_rule([4], [1], False)

        program2 = """
        {a}.
        {b}.
        c :- a.
        __x4 :- a.
        #project c.
        """     

        self.assertEqual(sorted(str(self.control.ground_program).replace(' ','').replace('\n','').split('.')), sorted(program2.replace(' ','').replace('\n','').split('.')))


    def test_parsing_theory_atoms(self):
        program = """
            a :- &k{b}.
        """

        def test(stm):
            if stm.ast_type == _ast.ASTType.Rule:
                literal = stm.body[0]
                self.assertEqual(literal.ast_type, _ast.ASTType.Literal)
                self.assertEqual(literal.atom.ast_type, _ast.ASTType.TheoryAtom)
        
        clingo.ast.parse_string(program, test)



