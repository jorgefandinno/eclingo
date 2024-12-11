import argparse

parser = argparse.ArgumentParser(description="Parse a program")
parser.add_argument("files", nargs="+", help="The files which should be converted.")
args = parser.parse_args()


from clingo.ast import AST, Function, TheoryAtom, Transformer

from eclingo.parsing.parser import parse_program


class K15Transformer(Transformer):
    def __init__(self):
        self.auxiliary_rules = []

    def visit_TheoryAtom(self, atom, loc="body"):
        if atom.term.name == "k" and not atom.term.arguments:
            new_atom = TheoryAtom(
                atom.location,
                Function(atom.location, "m", [], 0),
                elements=[Function(atom.location, "__k", atom.elements, 0)],
                guard=atom.guard,
            )
            return new_atom
        return atom


transformer = K15Transformer()


def print_k15(stm: AST) -> None:
    new_stm = transformer.visit(stm)
    print(new_stm)


def main():
    program_str = ""
    for file in args.files:
        if file != "-":
            with open(file, "r") as f:
                program_str += f.read()
    if "-" in args.files:
        program_str += input()
    parse_program(program_str, print_k15, only_m_normal_form=True)


if __name__ == "__main__":
    main()
