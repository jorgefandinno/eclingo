from typing import Sequence

from clingo import Function, Symbol
from clingo.ast import Sign

import eclingo.internal_states.internal_control as internal_control
from eclingo.literals import Literal
from eclingo.solver.candidate import Candidate

from .candidate import Candidate
from .world_view import EpistemicLiteral, WorldView


class WorldWiewBuilderReification:
    def __init__(self):
        self.control = internal_control.InternalStateControl(["0"], message_limit=0)
        self.control.configuration.solve.models = 0
        self.control.configuration.solve.project = "auto,3"
        print("WORLD_VIEW_BUILDER")

    def __call__(self, candidate: Candidate):
        print("Received candidates: ", candidate)
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
        # Check for explicit negation
        is_explicit = literal_symbol.positive

        arguments: Sequence[Symbol] = []
        if literal_symbol.arguments:
            for args in literal_symbol.arguments:
                arguments.append(args)

        new_symbol = Function(literal_symbol.name, arguments, is_explicit)
        literal = Literal(new_symbol, sign)

        return EpistemicLiteral(literal, Sign.NoSign, True)

    def world_view_from_candidate(self, candidate: Candidate):
        epistemic_literals = []
        k_symbols = []

        for epistemic_literal in candidate.pos:
            #print("\n The epistemic literal POS: ", epistemic_literal)
            show_literal = self.generate_k_symbol(epistemic_literal)
            if show_literal is not None:
                epistemic_literals.append(show_literal)
                k_symbols.append(show_literal.objective_literal)

        for epistemic_literal in candidate.neg:
            #print("\n The epistemic literal NEG: ", epistemic_literal)
            show_literal = self.generate_m_symbol(epistemic_literal)

            if (
                show_literal is not None
                and show_literal.objective_literal not in k_symbols
            ):
                epistemic_literals.append(show_literal)

        return WorldView(epistemic_literals)
