import unittest

import clingo
from clingo import Function, Number


import eclingo.internal_states.internal_control as internal_control

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

    def test_doubleNegation(self):

        program = """
        {d}.
        e :- not not d.
        """

        expected = [
            "{d}.",
            "e :- not __x2.",
            "__x2 :- not d."
        ]
        
        expected = map(lambda x: x.lstrip().rstrip(), expected)

        self.control = internal_control.InternalStateControl()
        self.control.configuration.solve.project = "auto,3"
        self.control.configuration.solve.models  = 0

        self.control.add("base", [], program)
        self.control.ground([("base", [])])
        
        # Beautify for testing purposes
        ground_program = self.control.ground_program.pretty_str()                               
        ground_program = sorted(map(str, list(ground_program.split("\n"))))                   
        
        self.assertEqual(ground_program, sorted(expected))



