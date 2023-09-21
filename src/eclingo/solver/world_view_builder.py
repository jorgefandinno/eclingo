from typing import Sequence

import clingo
from clingo import Function, Symbol
from clingo.ast import Sign

from eclingo.literals import Literal
from eclingo.solver.candidate import Candidate

from .candidate import Candidate
from .world_view import EpistemicLiteral, WorldView


class WorldWiewBuilderReification:
    def __init__(self, control: clingo.Control, show_stm: Sequence[Symbol]):
        self.show_statements = show_stm
        self.control = control

    def __call__(self, candidate: Candidate):
        return self.world_view_from_candidate(candidate)

    def generate_k_symbol(self, epistemic_literal):
        ep_args = epistemic_literal.arguments[0]
        epistemic_name = ep_args.name  # not1, not2 or u

        # if symbol is of the form &k{not L} with L an explicit literal
        if epistemic_name == "not1":
            return None
        # if symbol is of the form &k{not not L} with L an explicit literal
        elif epistemic_name == "not2":
            literal_symbol = ep_args.arguments[0].arguments[0]
            sign = Sign.DoubleNegation
        # if symbol is of the form &k{L} with L an explicit literal
        else:
            literal_symbol = ep_args.arguments[0]  # literal symbol is L
            sign = Sign.NoSign

        # Check for explicit negation
        is_explicit = literal_symbol.positive

        # Check for arguments of literal
        arguments: Sequence[Symbol] = []
        if literal_symbol.arguments:
            for args in literal_symbol.arguments:
                arguments.append(args)

        # print("The args: ", literal_symbol.arguments[0])

        new_symbol = Function(literal_symbol.name, arguments, is_explicit)
        literal = Literal(new_symbol, sign)

        return EpistemicLiteral(literal, Sign.NoSign)

    def generate_m_symbol(self, epistemic_literal):
        ep_args = epistemic_literal.arguments[0]
        epistemic_name = ep_args.name  # not1, not2 or u

        # if symbol is of the form &k{not L} with L an explicit literal
        if epistemic_name == "not1":
            literal_symbol = ep_args.arguments[0].arguments[0]
            sign = Sign.NoSign
        # if symbol is of the form &k{not not L} with L an explicit literal
        else:
            return None

        return EpistemicLiteral(literal_symbol, Sign.NoSign, True)

    def world_view_from_candidate(self, candidate: Candidate):
        epistemic_literals = []
        k_symbols = []
        epistemic_show_literals = []

        for epistemic_literal in candidate.pos:
            # print("\n The epistemic literal POS: ", epistemic_literal)
            show_literal = self.generate_k_symbol(epistemic_literal)
            if show_literal is not None:
                epistemic_literals.append(show_literal)
                k_symbols.append(show_literal.objective_literal)

                if epistemic_literal in self.show_statements:
                    epistemic_show_literals.append(show_literal)

        for epistemic_literal in candidate.neg:
            # print("\n The epistemic literal NEG: ", epistemic_literal)
            show_literal = self.generate_m_symbol(epistemic_literal)

            if (
                show_literal is not None
                and show_literal.objective_literal not in k_symbols
            ):
                epistemic_literals.append(show_literal)

                if epistemic_literal in self.show_statements:
                    epistemic_show_literals.append(show_literal)

        if epistemic_show_literals:
            return WorldView(epistemic_show_literals)

        return WorldView(epistemic_literals)


class WorldWiewBuilderReificationWithShow(WorldWiewBuilderReification):
    def __init__(self, reified_program):
        self.control = clingo.Control(["0"], message_limit=0)
        self.control.configuration.solve.models = 0
        self.control.configuration.solve.project = "auto,3"
        self.reified_program = reified_program
        self.show_statements: Sequence[Symbol] = []

        program_meta_encoding = """
                                symbolic_atom(SA, A) :- output(SA,LT), #count{LL : literal_tuple(LT, LL)} = 1, literal_tuple(LT, A).
                                show_statement(SA) :- symbolic_atom(show_statement(SA), _).

                                {k(A)} :- output(k(A), _).
                                """

        self.control.add("base", [], self.reified_program)
        self.control.add("base", [], program_meta_encoding)
        self.control.ground([("base", [])])

        super().__init__(self.control, self.show_statements)

    def world_view_from_candidate(self, candidate: Candidate):
        candidate_pos = candidate[0]
        candidate_neg = candidate[1]
        candidate_assumptions = []
        cand_show = []

        for literal in candidate[0]:
            assumption = (literal, True)
            candidate_assumptions.append(assumption)
            literal = literal.arguments[0]
            cand_show.append(literal)

        for literal in candidate[1]:
            assumption = (literal, False)
            candidate_assumptions.append(assumption)
            literal = literal.arguments[0]
            cand_show.append(literal)

        self.control.configuration.solve.models = 0
        self.control.configuration.solve.project = "no"

        with self.control.solve(
            yield_=True, assumptions=candidate_assumptions
        ) as handle:
            model = None
            for model in handle:
                pass

            assert model is not None
            self.epistemic_show_statements(model, cand_show)

        return super().world_view_from_candidate(
            Candidate(candidate_pos, candidate_neg)
        )

    """
        Check in model for show_statement(X) facts for all X atoms.
    """

    def epistemic_show_statements(self, model, candidates_show):
        show_name: str = "show_statement"

        for atom in candidates_show:
            show_arguments: Sequence[Symbol] = []
            atom_arguments: Sequence[Symbol] = []

            if (
                atom.name == "not1" or atom.name == "not2"
            ):  # Check if it is a negative atom
                atom_show = atom.arguments[0].arguments[0]
            else:
                atom_show = atom.arguments[0]

            # Check for arguments of atom
            if atom_show.arguments:
                for args in atom_show.arguments:
                    atom_arguments.append(args)

            show_arguments.append(
                Function(atom_show.name, atom_arguments, atom.arguments[0].positive)
            )

            show_stm = Function(show_name, show_arguments, True)

            k_atom = Function("k", [atom], atom.arguments[0].positive)
            if model.contains(show_stm) and k_atom not in self.show_statements:
                self.show_statements.append(k_atom)
