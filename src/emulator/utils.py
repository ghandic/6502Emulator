from operator import eq
from typing import Callable, List


def switch(value: object, comp: Callable = eq) -> List[Callable]:
    return [lambda match: comp(match, value)]
