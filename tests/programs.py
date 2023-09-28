from typing import NamedTuple, Optional, Union


class Program(NamedTuple):
    program: str
    non_ground_reification: Optional[str] = None
    ground_reification: Optional[str] = None
    candidates_00: Optional[str] = None  # candidates without fact optimization
    candidates_01: Optional[str] = None  # candidates with fact optimization
    candidates_02: Optional[str] = None  # candidates with fast preprocessing
    candidates_wv: Optional[str] = None  # world view as candidates objects
    fast_preprocessing: Optional[
        Union[str, tuple[str, str]]
    ] = None  # the result of fast preprocessing, if a string both lower and upper are the same
    has_fast_preprocessing: bool = False
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
        candidates_01=[("k(a)", "a")],
        fast_preprocessing="a b k(a)",
        has_fast_preprocessing=True,
    ),
    Program(
        description="",
        program="a. b :- &k{a}. c :- &k{b}.",
        candidates_01=[("k(a) not1(k(b))", "a"), ("k(a) k(b)", "a")],
        candidates_02=[("k(a) k(b)", "a")],
        fast_preprocessing="a b c k(a) k(b)",
        has_fast_preprocessing=True,
    ),
    Program(
        description="",
        program="{a}. b :- &k{a}.",
        non_ground_reification="{u(a)}. u(b) :- k(u(a)). { k(u(a)) } :- u(a).",
        candidates_00=[
            "k(a)",
            "not1(k(a))",
        ],
        fast_preprocessing=("", "a b k(a)"),
        has_fast_preprocessing=True,
    ),
    Program(
        description="",
        program="{a}. b :- &k{a}. :- not b.",
        non_ground_reification="""
            {u(a)}.
            u(b) :- k(u(a)).
            { k(u(a)) } :- u(a).
            :- not u(b).
            """,
        candidates_00=[
            ("k(a)", ""),
        ],
        fast_preprocessing=("b k(a)", "a b k(a)"),
        has_fast_preprocessing=True,
    ),
    Program(
        description="",
        program="{a}. :- not a. b :- &k{a}.",
        non_ground_reification="{u(a)}. :- not u(a). u(b) :- k(u(a)). { k(u(a)) } :- u(a).",
        candidates_00=[
            "k(a)",
            "not1(k(a))",
        ],
        candidates_02=[
            "k(a)",
        ],
        fast_preprocessing=("a b k(a)", "a b k(a)"),
        has_fast_preprocessing=True,
    ),
    Program(
        description="",
        program="{a}. :- a. b :- &k{a}.",
        non_ground_reification="{u(a)}. :- u(a). u(b) :- k(u(a)). { k(u(a)) } :- u(a).",
        # candidates_00=[
        #     "k(a)",
        #     "not1(k(a))",
        # ],
        candidates_01=[
            "not1(k(a))",
        ],
        fast_preprocessing="",
        has_fast_preprocessing=True,
    ),
    Program(
        description="",
        program="a. b :- &k{not a}.",
        candidates_00=[
            "",
        ],
        fast_preprocessing="a",
        has_fast_preprocessing=True,
    ),
    Program(
        description="",
        program="{a}. b :- &k{not a}.",
        candidates_01=[
            "k(not1(a))",
            "not1(k(not1(a)))",
        ],
        fast_preprocessing=("", "a b not1(a) k(not1(a))"),
        has_fast_preprocessing=True,
    ),
    Program(
        description="",
        program="{a}. :- not a. b :- &k{not a}.",
        candidates_01=[
            "not1(k(not1(a)))",
        ],
        fast_preprocessing="a",
        has_fast_preprocessing=True,
    ),
    Program(
        description="",
        program="{a}. :- a. b :- &k{not a}.",
        candidates_01=[
            "k(not1(a))",
            "not1(k(not1(a)))",
        ],
        candidates_02=[
            "k(not1(a))",
        ],
        fast_preprocessing="b not1(a) k(not1(a))",
        has_fast_preprocessing=True,
    ),
    Program(
        description="",
        program="{a}. {b}. :- not a. :- not b. c :- &k{a}, &k{b}.",
        candidates_01=[
            "not1(k(a)) not1(k(b))",
            "not1(k(a)) k(b)",
            "k(a) not1(k(b))",
            "k(a) k(b)",
        ],
        candidates_02=[
            "k(a) k(b)",
        ],
        fast_preprocessing="a b c k(a) k(b)",
        has_fast_preprocessing=True,
    ),
    Program(
        description="",
        program="{a}. {b}. :- not a, not b. :- a, not b. :- b, not a. c :- &k{a}, &k{b}.",
        candidates_01=[
            "not1(k(a)) not1(k(b))",
            "not1(k(a)) k(b)",
            "k(a) not1(k(b))",
            "k(a) k(b)",
        ],
        fast_preprocessing=("", "a b c k(a) k(b)"),
        has_fast_preprocessing=True,
    ),
    Program(
        description="",
        program="a. :- a.",
        candidates_01=[],
        fast_preprocessing=None,
        has_fast_preprocessing=True,
    ),
    Program(
        description="",
        program="a. b :- &k{a}. :- b.",
        candidates_01=[],
        fast_preprocessing=None,
        has_fast_preprocessing=True,
    ),
]
