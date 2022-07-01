from typing import List, NamedTuple
from clingo import Symbol

class Candidate(NamedTuple):
    pos: List[Symbol]
    neg: List[Symbol]

    