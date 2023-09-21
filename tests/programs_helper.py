from typing import List, NamedTuple, Optional

from eclingo.solver.candidate import Candidate


class Program(NamedTuple):
    program: Optional[str]
    non_ground_reification: Optional[str] = None
    ground_reification: Optional[str] = None
    candidates_00_str: Optional[List[str]] = None
    candidates_00: Optional[List[Candidate]] = None
    candidates_01_str: Optional[List[str]] = None
    candidates_01: Optional[List[Candidate]] = None
    candidates_wv_str: Optional[List[str]] = None
    candidates_wv: Optional[List[Candidate]] = None
    description: str = ""
