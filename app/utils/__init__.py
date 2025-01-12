import secrets
from enum import Enum
from typing import Dict, List, Optional, TypeVar

S = TypeVar('S', bound=Enum)


def random_from_enum(
    choices: S,
    weight: Optional[Dict[S, int]] = None
) -> S:

    available_choices = list(choices)

    if weight is None:
        return secrets.choice(available_choices)

    for item in weight:
        choices.extend([item] * weight[item])

    return secrets.choice(available_choices)


T = TypeVar('T')


def random_from_list(
    data:  List[T],
    weight: Optional[Dict[T, int]] = None
) -> T:

    if weight is None:
        return secrets.choice(data)

    choices = data

    for item in weight:
        choices.extend([item] * weight[item])

    return secrets.choice(choices)

