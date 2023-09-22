from typing import NamedTuple, Optional


class Program(NamedTuple):
    program: str
    non_ground_reification: Optional[str] = None
    ground_reification: Optional[str] = None
    candidates_00: Optional[str] = None  # candidates without fact optimization
    candidates_01: Optional[str] = None  # candidates with fact optimization
    candidates_02: Optional[str] = None  # candidates with fast preprocessing
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
        candidates_01=[("k(a)", "a")],
    ),
    Program(
        description="",
        program="{a}. b :- &k{a}.",
        non_ground_reification="{u(a)}. u(b) :- k(u(a)). { k(u(a)) } :- u(a).",
        candidates_00=[
            "k(a)",
            "not1(k(a))",
        ],
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
    ),
    # Program(
    #     description="",
    #     program="{a}. :- not a. b :tes- &k{a}.",
    #     non_ground_reification="{u(a)}. :- not u(a). u(b) :- k(u(a)). { k(u(a)) } :- u(a).",
    #     candidates_00=[
    #         "k(a)",
    #         "not1(k(a))",
    #     ],
    #     candidates_02=[
    #         "k(a)",
    #     ],
    # ),
    # Program(
    #     description="",
    #     program="{a}. :- a. b :- &k{a}.",
    #     non_ground_reification="{u(a)}. :- u(a). u(b) :- k(u(a)). { k(u(a)) } :- u(a).",
    #     # candidates_00=[
    #     #     "k(a)",
    #     #     "not1(k(a))",
    #     # ],
    #     candidates_01=[
    #         "not1(k(a))",
    #     ],
    # ),
    # Program(
    #     description="",
    #     program="a. b :- &k{not a}.",
    #     non_ground_reification="u(a). u(b) :- k(not1(u(a))). { k(not1(u(a))) } :- not1(u(a)). not1(u(a)) :- not u(a).",
    #     candidates_00=[
    #         "",
    #     ],
    # ),
    # Program(
    #     description="",
    #     program="{a}. b :- &k{not a}.",
    #     non_ground_reification="{u(a)}. u(b) :- k(not1(u(a))). { k(not1(u(a))) } :- not1(u(a)). not1(u(a)) :- not u(a).",
    #     candidates_01=[
    #         "k(not1(a))",
    #         "not1(k(not1(a)))",
    #     ],
    # ),
    # Program(
    #     description="",
    #     program="{a}. :- not a. b :- &k{not a}.",
    #     non_ground_reification="{u(a)}. :- not u(a). u(b) :- k(not1(u(a))). { k(not1(u(a))) } :- not1(u(a)). not1(u(a)) :- not u(a).",
    #     candidates_01=[
    #         "not1(k(not1(a)))",
    #     ],
    # ),
    # Program(
    #     description="",
    #     program="{a}. :- a. b :- &k{not a}.",
    #     non_ground_reification="{u(a)}. :- u(a). u(b) :- k(not1(u(a))). { k(not1(u(a))) } :- not1(u(a)). not1(u(a)) :- not u(a).",
    #     candidates_01=[
    #         "k(not1(a))",
    #         "not1(k(not1(a)))",
    #     ],
    #     candidates_02=[
    #         "k(not1(a))",
    #     ],
    # ),
    # Program(
    #     description="",
    #     program="a. b :- &k{a}. c :- &k{b}.",
    #     non_ground_reification="u(a). u(b) :- k(u(a)). { k(u(a)) } :- u(a).",
    #     candidates_00=[
    #         "k(a)",
    #         "not1(k(a))",
    #     ],
    #     candidates_01=[
    #         "k(a)",
    #     ],
    # ),
]
