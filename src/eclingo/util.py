"""
Utility functions.
"""

from typing import Any, Callable, Iterable, List, Tuple, TypeVar

from eclingo.config import AppConfig
from eclingo.parsing import parser

T = TypeVar("T")


def partition1(
    iterable: Iterable[T], pred: Callable[[T], bool], fun: Callable[[T], Any]
) -> Tuple[List[T], List[T]]:
    """
    Partitions iterable according to *pred.
    fun is applied to each element.
    """

    l0: List[T] = []
    other: List[T] = []
    l0_append = l0.append
    other_append = other.append
    for item in iterable:
        if pred(item):
            l0_append(fun(item))
        else:
            other_append(fun(item))
    return l0, other


def partition2(
    iterable: Iterable[T],
    pred0: Callable[[T], bool],
    pred1: Callable[[T], bool],
    fun: Callable[[T], Any],
) -> Tuple[List[T], List[T], List[T]]:
    """
    Partitions iterable according to *pred.
    fun is applied to each element.
    """

    l0: List[T] = []
    l1: List[T] = []
    other: List[T] = []
    l0_append = l0.append
    l1_append = l1.append
    other_append = other.append
    for item in iterable:
        if pred0(item):
            l0_append(fun(item))
        elif pred1(item):
            l1_append(fun(item))
        else:
            other_append(fun(item))
    return l0, l1, other


def partition3(
    iterable: Iterable[T],
    pred0: Callable[[T], bool],
    pred1: Callable[[T], bool],
    pred2: Callable[[T], bool],
    fun: Callable[[T], Any],
) -> Tuple[List[T], List[T], List[T], List[T]]:
    """
    Partitions iterable according to *pred.
    fun is applied to each element.
    """

    l0: List[T] = []
    l1: List[T] = []
    l2: List[T] = []
    other: List[T] = []
    l0_append = l0.append
    l1_append = l1.append
    l2_append = l2.append
    other_append = other.append
    for item in iterable:
        if pred0(item):
            l0_append(fun(item))
        elif pred1(item):
            l1_append(fun(item))
        elif pred2(item):
            l2_append(fun(item))
        else:
            other_append(fun(item))
    return l0, l1, l2, other


def partition4(  # pylint: disable-msg=too-many-locals
    iterable: Iterable[T],
    pred0: Callable[[T], bool],
    pred1: Callable[[T], bool],
    pred2: Callable[[T], bool],
    pred3: Callable[[T], bool],
    fun: Callable[[T], Any],
) -> Tuple[List[T], List[T], List[T], List[T], List[T]]:
    """
    Partitions iterable according to *pred.
    fun is applied to each element.
    """

    l0: List[T] = []
    l1: List[T] = []
    l2: List[T] = []
    l3: List[T] = []
    other: List[T] = []
    l0_append = l0.append
    l1_append = l1.append
    l2_append = l2.append
    l3_append = l3.append
    other_append = other.append
    for item in iterable:
        if pred0(item):
            l0_append(fun(item))
        elif pred1(item):
            l1_append(fun(item))
        elif pred2(item):
            l2_append(fun(item))
        elif pred3(item):
            l3_append(fun(item))
        else:
            other_append(fun(item))
    return l0, l1, l2, l3, other


def partition(
    iterable: Iterable[T],
    *pred: Callable[[T], bool],
    fun: Callable[[T], Any] = lambda x: x
) -> Tuple[List[T], ...]:
    """
    Partitions iterable according to *pred.
    fun is applied to each element.
    """
    if len(pred) == 4:
        return partition4(iterable, pred[0], pred[1], pred[2], pred[3], fun)
    if len(pred) == 1:
        return partition1(iterable, pred[0], fun)
    if len(pred) == 2:
        return partition2(iterable, pred[0], pred[1], fun)
    if len(pred) == 3:
        return partition3(iterable, pred[0], pred[1], pred[2], fun)

    lists: Tuple[List[T], ...] = tuple([] for _ in range(len(pred) + 1))
    appends = tuple(li.append for li in lists)
    for item in iterable:
        added = False
        for i, p in enumerate(pred):
            if p(item):
                appends[i](fun(item))
                added = True
                break
        if not added:
            appends[-1](fun(item))
    return lists


# def flatten(lst):
#     """Helping function to parse program for flag: --output-e=rewritten"""
#     result = []
#     for lst2 in lst:
#         result.append(lst2)

#     return result


def parse_program(stm, parameters=None, name="base"):
    """Helping function to parse program for flag: --output-e=rewritten"""
    if parameters is None:
        parameters = []
    ret = []
    parser.parse_program(
        stm,
        ret.append,
        parameters,
        name,
        config=AppConfig(semantics="c19-1", verbose=0),
    )
    return ret
