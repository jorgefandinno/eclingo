import unittest
from clingo import ast
from eclingo.parsing import parser

def flatten(lst):
    result = []
    for lst2 in lst:
        if isinstance(lst2, list):
            for e in lst2:
                result.append(str(e))
        else:
            result.append(str(lst2))
        
    return result

def parse_program(stm, parameters=[], name="base"):
    ret = []
    parser.parse_program(stm, ret.append, parameters, name)
    return flatten(ret)

def reify_parse_program(stm, parameters=[], name="base"):
    ret = []
    parser.reify_parse_program(stm, ret.append, parameters, name)
    return flatten(ret)

def clingo_parse_program(stm):
    ret = []
    ast.parse_string(stm, ret.append)
    ret = [str(rule) for rule in ret]
    return ret

class TestCase(unittest.TestCase):

    def setUp(self):
        self.print = False

    def assert_equal_program(self, program, expected):
        expected_program = clingo_parse_program(expected)
        if self.print:
            print("--- program ---")
            print(ast_repr(program))
            print("--- expected program ---")
            print(ast_repr(expected_program))
        self.assertListEqual(sorted(program), sorted(expected_program))

class Test(TestCase):

    def test_epistemic_atom(self):
        self.assert_equal_program(reify_parse_program(":- &k{a}."), ":- k_u(a). {k_u(a)} :- u(a).")

    def test_epistemic_atom_with_strong_negation(self):
        # Deal with the negated symbols -> Maybe on the reify_symbolic_atoms we have to deal for the case when storn negation of literal
        # self.assert_equal_program(reify_parse_program(":- &k{-a}."), ":- k_sn_u(a). sn_u(a) :- -u(a). {k_sn_u(a)} :- sn_u(a).")
        self.assert_equal_program(reify_parse_program(":- &k{- -a}."), ":- k_u(a). {k_u(a)} :- u(a).")

    def test_epistemic_atom_with_default_negation(self):
        self.assert_equal_program(reify_parse_program(":- &k{ not a}."), ":- k_not_u(a). not_u(a) :- not u(a). {k_not_u(a)} :- not_u(a).")
        self.assert_equal_program(reify_parse_program("b :- &k{ not a}."), "u(b) :- k_not_u(a). not_u(a) :- not u(a). {k_not_u(a)} :- not_u(a).")
        self.assert_equal_program(reify_parse_program(":- &k{ not not a}."), ":- k_not2_u(a). not2_u(a) :- not not u(a). {k_not2_u(a)} :- not2_u(a).")

    def test_epistemic_atom_with_both_negations(self):
        #self.assert_equal_program(reify_parse_program(":- &k{ not -a}."), ":- k_not_sn_u(a). not_sn_u(a) :- not sn_u(a). {k_not_sn_u(a)} :- not_sn_u(a). sn_u(a) :- -u(a).")
        self.assert_equal_program(parse_program(":- &k{ not not -a}."), ":- k_not2_sn_u_a. not2_sn_u_a :- not not sn_u_a.  {k_not2_sn_u_a} :- not2_sn_u_a. sn_u_a :- -u_a.")

# Changed above
######################################################
# Not changed below

    def test_epistemic_with_variables(self):
        self.assert_equal_program(parse_program(":- &k{a(V0)}."), ":- k_u_a(V0). {k_u_a(V0)} :- u_a(V0).")
        self.assert_equal_program(parse_program(":- &k{-a(V0)}."), ":- k_sn_u_a(V0). sn_u_a(V0) :- -u_a(V0). {k_sn_u_a(V0)} :- sn_u_a(V0).")
        self.assert_equal_program(parse_program(":- &k{- -a(V0)}."), ":- k_u_a(V0). {k_u_a(V0)} :- u_a(V0).")
        self.assert_equal_program(parse_program(":- &k{ not a(V0)}."), ":- k_not_u_a(V0). not_u_a(V0) :- not u_a(V0). {k_not_u_a(V0)} :- not_u_a(V0).")
        self.assert_equal_program(parse_program(":- &k{ not not a(V0)}."), ":- k_not2_u_a(V0). not2_u_a(V0) :- not not u_a(V0). {k_not2_u_a(V0)} :- not2_u_a(V0).")
        self.assert_equal_program(parse_program(":- &k{ not -a(V0)}."), ":- k_not_sn_u_a(V0). not_sn_u_a(V0) :- not sn_u_a(V0). {k_not_sn_u_a(V0)} :- not_sn_u_a(V0). sn_u_a(V0) :- -u_a(V0).")
        self.assert_equal_program(parse_program(":- &k{ not not -a(V0)}."), ":- k_not2_sn_u_a(V0). not2_sn_u_a(V0) :- not not sn_u_a(V0).  {k_not2_sn_u_a(V0)} :- not2_sn_u_a(V0). sn_u_a(V0) :- -u_a(V0).")

    def test_epistemic_with_variables_safety01(self):
        self.assert_equal_program(parse_program(":- &k{a(V0)}, not b(V0)."), """
            :- k_u_a(V0), not u_b(V0).
            { k_u_a(V0) :  } :- u_a(V0).
            """)

    def test_epistemic_with_variables_safety02(self):
        self.assert_equal_program(parse_program(":- a(V0), &k{not b(V0)}."), """
            :- u_a(V0), k_not_u_b(V0).
            not_u_b(V0) :- u_a(V0), not u_b(V0).
            { k_not_u_b(V0) :  } :- not_u_b(V0).
            """)

    def test_epistemic_with_variables_safety03(self):
        self.assert_equal_program(parse_program(":- &k{a(V0)}, &k{not b(V0)}."), """
            :- k_u_a(V0), k_not_u_b(V0).
            not_u_b(V0) :- k_u_a(V0), not u_b(V0).
            { k_not_u_b(V0) :  } :- not_u_b(V0).
            { k_u_a(V0) :  } :- u_a(V0).
            { k_u_a(V0) :  } :- u_a(V0).
            """)
    # Note that the last two rules appear repeated. The second copy apears when processing the rules
    # not_u_b(V0) :- &k{u_a(V0)}, not u_b(V0).
    # An improvement would removing those unecessary rules

    def test_epistemic_with_variables_safety04(self):
            self.assert_equal_program(parse_program('b :- not not &k{a(X)}.'), """
            u_b :- not not k_u_a(X).
            { k_u_a(X) : } :- u_a(X).
            """)

    def test_negated_epistemic_literals(self):
        self.assert_equal_program(parse_program(":- not &k{a(V0)}, &k{b(V0)}."), """
            :- not k_u_a(V0), k_u_b(V0).
            {k_u_a(V0)} :- u_a(V0).
            {k_u_b(V0)} :- u_b(V0).
            """)
        self.assert_equal_program(parse_program(":- not not &k{a(V0)}, &k{b(V0)}."), """
            :- not not k_u_a(V0), k_u_b(V0).
            {k_u_a(V0)} :- u_a(V0).
            {k_u_b(V0)} :- u_b(V0).
            """)

    def test_weighted_rules(self):
        self.assert_equal_program(parse_program(":-{a} = 0."), ":-{u_a} = 0.")

    def test_parameters01(self):
        self.assert_equal_program(parse_program("a(1..n).", ["n"], "parametrized" ), "#program parametrized(n). u_a(1..n).")

    def test_parameters02(self):
        self.assert_equal_program(parse_program("a(1..n).", ["n"], "base" ), "#program base(n). u_a(1..n).")

    def test_heuristic(self):
        self.assert_equal_program(parse_program("#heuristic a. [1,sign]", [], "base" ), "#heuristic u_a. [1,sign]")

    
