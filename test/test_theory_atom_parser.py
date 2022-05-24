import unittest
from typing import Callable, List, Optional, Sequence, cast
import clingo
from clingo import ast
from clingo.symbol import Function
from clingo.ast import AST, ASTType, Location, Position, Transformer, parse_string, Variable
from clingox.ast import TheoryParser, theory_parser_from_definition

theory = '''#theory eclingo {
    default_negation { not : 0, unary};
    &k/0 : default_negation, body
}.
'''

theory_parse = None
def extract(stm):
    if stm.ast_type == ASTType.TheoryDefinition:
        global theory_parse
        theory_parse = theory_parser_from_definition(stm)
parse_string(theory, extract)


class Extractor(Transformer):
    '''
    Simple visitor returning the first theory term in a program.
    '''
    # pylint: disable=invalid-name
    atom: Optional[AST]

    def __init__(self, parse:bool=False):
        self.atom = None
        self.parse = parse

    def visit_TheoryAtom(self, x: AST):
        '''
        Extract theory atom.
        '''
        if self.parse:
            x = theory_parse.visit(x)
        self.atom = x
        return x


def theory_atom(s: str, mode: int=0) -> AST:
    """
    Convert string to theory term.
    """
    if mode==2:
        v = Extractor(parse=True)
    else:
        v = Extractor()

    def visit(stm):
        v(stm)

    if mode==0 or mode==2:
        clingo.ast.parse_string(f"{s}.", visit)
    elif mode==1:
        clingo.ast.parse_string(theory + f"{s}.", visit)
    return cast(AST, v.atom)


class TesterCase(unittest.TestCase):

    def test_theory_parse(self):
        theory_atom_str = '&k{ a }'
        location = Location(begin=Position(filename='<string>', line=1, column=5), end=Position(filename='<string>', line=1, column=6))
        element = ast.TheoryAtomElement([ast.SymbolicTerm(location, Function('a', [], True))], [])
        result = theory_atom(theory_atom_str).elements[0]
        self.assertEqual(result, element)

        theory_atom_str = '&k{ a(X) }'
        location1 = Location(begin=Position(filename='<string>', line=1, column=5), end=Position(filename='<string>', line=1, column=9))
        location2 = Location(begin=Position(filename='<string>', line=1, column=7), end=Position(filename='<string>', line=1, column=8))
        element = ast.TheoryAtomElement([ast.TheoryFunction(location1, 'a', [ast.Variable(location2, 'X')])], [])
        result = theory_atom(theory_atom_str).elements[0]
        self.assertEqual(result, element)

        theory_atom_str = '&k{ not a(X) }'
        location1 = Location(begin=Position(filename='<string>', line=1, column=5), end=Position(filename='<string>', line=1, column=13))
        location2 = Location(begin=Position(filename='<string>', line=1, column=9), end=Position(filename='<string>', line=1, column=13))
        location3 = Location(begin=Position(filename='<string>', line=1, column=11), end=Position(filename='<string>', line=1, column=12))
        element = ast.TheoryAtomElement([ast.TheoryUnparsedTerm(location1, [ast.TheoryUnparsedTermElement(['not'], ast.TheoryFunction(location2, 'a', [ast.Variable(location3, 'X')]))])], [])
        result = theory_atom(theory_atom_str).elements[0]
        self.assertEqual(result, element)

    def test_theory_parse_with_theory(self):
        theory_atom_str = '&k{ a }'
        location = Location(begin=Position(filename='<string>', line=1, column=5), end=Position(filename='<string>', line=1, column=6))
        element = ast.TheoryAtomElement([ast.SymbolicTerm(location, Function('a', [], True))], [])
        result = theory_atom(theory_atom_str, mode=1).elements[0]
        self.assertEqual(result, element)

        theory_atom_str = '&k{ a(X) }'
        location1 = Location(begin=Position(filename='<string>', line=1, column=5), end=Position(filename='<string>', line=1, column=9))
        location2 = Location(begin=Position(filename='<string>', line=1, column=7), end=Position(filename='<string>', line=1, column=8))
        element = ast.TheoryAtomElement([ast.TheoryFunction(location1, 'a', [ast.Variable(location2, 'X')])], [])
        result = theory_atom(theory_atom_str, mode=1).elements[0]
        self.assertEqual(result, element)

        theory_atom_str = '&k{ not a(X) }'
        location1 = Location(begin=Position(filename='<string>', line=1, column=5), end=Position(filename='<string>', line=1, column=13))
        location2 = Location(begin=Position(filename='<string>', line=1, column=9), end=Position(filename='<string>', line=1, column=13))
        location3 = Location(begin=Position(filename='<string>', line=1, column=11), end=Position(filename='<string>', line=1, column=12))
        element = ast.TheoryAtomElement([ast.TheoryUnparsedTerm(location1, [ast.TheoryUnparsedTermElement(['not'], ast.TheoryFunction(location2, 'a', [ast.Variable(location3, 'X')]))])], [])
        result = theory_atom(theory_atom_str, mode=1).elements[0]
        self.assertEqual(result, element)

    def test_theory_parse_with_clingox_theory(self):
        theory_atom_str = '&k{ a }'
        location = Location(begin=Position(filename='<string>', line=1, column=5), end=Position(filename='<string>', line=1, column=6))
        element = ast.TheoryAtomElement([ast.SymbolicTerm(location, Function('a', [], True))], [])
        result = theory_atom(theory_atom_str, mode=2).elements[0]
        self.assertEqual(result, element)

        theory_atom_str = '&k{ a(X) }'
        location1 = Location(begin=Position(filename='<string>', line=1, column=5), end=Position(filename='<string>', line=1, column=9))
        location2 = Location(begin=Position(filename='<string>', line=1, column=7), end=Position(filename='<string>', line=1, column=8))
        element = ast.TheoryAtomElement([ast.TheoryFunction(location1, 'a', [ast.Variable(location2, 'X')])], [])
        result = theory_atom(theory_atom_str, mode=2).elements[0]
        self.assertEqual(result, element)

        theory_atom_str = '&k{ not a(X) }'
        location1 = Location(begin=Position(filename='<string>', line=1, column=9), end=Position(filename='<string>', line=1, column=13))
        location2 = Location(begin=Position(filename='<string>', line=1, column=9), end=Position(filename='<string>', line=1, column=13))
        location3 = Location(begin=Position(filename='<string>', line=1, column=11), end=Position(filename='<string>', line=1, column=12))
        element = ast.TheoryAtomElement([ast.TheoryFunction(location1, 'not', [ast.TheoryFunction(location2, 'a', [ast.Variable(location3, 'X')])])], [])
        result = theory_atom(theory_atom_str, mode=2).elements[0]
        print(repr(result))
        self.assertEqual(result, element)
        
