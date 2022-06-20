import unittest

import clingo
from clingo import Function, Number

import eclingo.util.clingoext as clingoext
from eclingo.util.logger import silent_logger

from eclingo.util.groundprogram import ClingoOutputAtom, ClingoProject, ClingoRule, GroundProgram, PrettyGroundProgram


class Test(unittest.TestCase):


    def test_clingo_symbol_function(self):
        symbol=Function("b", [Number(1)], True)
        # p=PrettyGroundProgram(symbol)

        self.assertEqual(str(symbol), 'b(1)')


    def test_clingo_output_atom_pretty(self):
        
        s = [ClingoOutputAtom(symbol=Function("b", [Number(1)], True), atom=0, order=0)]
        p = PrettyGroundProgram(s)

        self.assertEqual(str(p),'b(1).')

    # Functionality works. On change ground_program from clingox() the test failed because of how the parsing for asserting was being done.
    def test_doubleNegation(self):

        program = """
        {d}.
        e :- not not d.
        """

        #expected = """ 
        #{d}.
        #e :- not x_2.
        #x_2 :- not d.
        #"""

        # Try to set it up for clean (I changed x_2 -> __x2) -> Just checking, the ground works, but it ground variables weirdly
        new_expected = [
            "{d}.",
            "e :- not __x2.",
            "__x2 :- not d."
        ]
        new_expected = map(lambda x: x.lstrip().rstrip(), new_expected)

        self.control = clingoext.Control(logger=silent_logger)
        self.control.configuration.solve.project = "auto,3"
        self.control.configuration.solve.models  = 0

        self.control.add("base", [], program)
        self.control.ground([("base", [])])
        
        # Beautify for testing purposes
        ground_program = self.control.ground_program.pretty_str()                               
        ground_program = sorted(map(str, list(ground_program.split("\n"))))                   
        
        # The answer is correct but the way it is parsed is wrong, why changes it to be __x2 instad of x_2 
        # Has to do with how parsing works (?)
        
        # New testing -> Works
        self.assertEqual(ground_program, sorted(new_expected))



