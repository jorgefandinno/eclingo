import unittest
from clingo import Function
from clingo.control import Control
from clingox.program import Program, ProgramObserver, Remapping, Fact, Rule

program = Program(output_atoms={}, shows=[], facts=[Fact(symbol=Function('u_a', [], True))], rules=[Rule(choice=False, head=[1], body=[])], weight_rules=[], heuristics=[], edges=[], minimizes=[], externals=[], projects=None, assumptions=[])

class TestExamples(unittest.TestCase):

    def test_program(self):
        self.assertEqual(program.output_atoms, {})
        self.assertEqual(program.shows, [])
        self.assertEqual(program.facts, [Fact(symbol=Function('u_a', [], True))])
        self.assertEqual(program.rules, [Rule(choice=False, head=[1], body=[])])
        self.assertEqual(program.weight_rules, [])
        self.assertEqual(program.heuristics, [])
        self.assertEqual(program.edges, [])
        self.assertEqual(program.minimizes, [])
        self.assertEqual(program.externals, [])
        self.assertEqual(program.projects, None)
        self.assertEqual(program.assumptions, [])
        self.assertEqual(program.__str__(), 'u_a.\n__x1.')
        self.assertEqual(program.__repr__(), "Program(output_atoms={}, shows=[], facts=[Fact(symbol=Function('u_a', [], True))], rules=[Rule(choice=False, head=[1], body=[])], weight_rules=[], heuristics=[], edges=[], minimizes=[], externals=[], projects=None, assumptions=[])")
        self.assertEqual(program.__eq__(program), True)
        self.assertEqual(program.__eq__(Program(output_atoms={}, shows=[], facts=[Fact(symbol=Function('u_a', [], True))], rules=[Rule(choice=False, head=[1], body=[])], weight_rules=[], heuristics=[], edges=[], minimizes=[], externals=[], projects=None, assumptions=[])), True)

        control = Control()
        with control.backend() as backend:
            mapping = Remapping(backend, program.output_atoms, program.facts)
            program.add_to_backend(backend, mapping)

        # with control.solve(yield_=True) as handle:
        #     for model in handle:
        #         print(model)