from typing import List, NamedTuple

from eclingo.solver.candidate import Candidate


class Program(NamedTuple):
    program: str
    non_ground_reification: str = None
    candidates: List[Candidate] = None
    wv_candidates: List[Candidate] = None
    unoptimiced_candidates: List[Candidate] = None
    ground_reification: str = None
    description: str = ""
