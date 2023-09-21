from typing import NamedTuple, Optional


class Program(NamedTuple):
    program: str
    non_ground_reification: Optional[str] = None
    ground_reification: Optional[str] = None
    candidates_00: Optional[str] = None  # candidates without fact optimization
    candidates_01: Optional[str] = None  # candidates with fact optimization
    candidates_wv: Optional[str] = None  # world view as candidates objects
    description: str = ""


program_list = [
    Program(
        description="",
        program="a. b :- &k{a}.",
        non_ground_reification="u(a). u(b) :- k(u(a)). { k(u(a)) } :- u(a).",
        candidates_00=[
            "k(a)",
            "not1(k(a))",
        ],
        candidates_01=[
            "k(a)",
        ],
    ),
    Program(
        description="",
        program="{a}. b :- &k{a}.",
        non_ground_reification="{u(a)}. u(b) :- k(u(a)). { k(u(a)) } :- u(a).",
        candidates_00=[
            "k(a)",
            "not1(k(a))",
        ],
        candidates_01=[
            "k(a)",
            "not1(k(a))",
        ],
    ),
]
