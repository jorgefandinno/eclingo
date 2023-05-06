from typing import List, NamedTuple

from clingo import Symbol


class Candidate(NamedTuple):
    pos: List[Symbol]
    neg: List[Symbol]

    def __str__(self):
        pos_s = ", ".join(str(s) for s in self.pos)
        neg_s = ", ".join(str(s) for s in self.neg)
        return f"Candidate(pos=[{pos_s}], neg=[{neg_s}])"
