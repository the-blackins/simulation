import secrets
from enum import Enum
from typing import Dict, List, Optional, TypeVar
from log.logger import logger  

S = TypeVar('S', bound=Enum)


def random_from_enum(
    choices: S,
    weight: Optional[Dict[S, int]] = None
) -> S:
    available_choices = list(choices)
    logger.debug(f"Random selection from enum called with choices: {available_choices} and weights: {weight}")

    if weight is None:
        selected = secrets.choice(available_choices)
        # logger.info(f"Selected {selected} from enum without weights")
        return selected

    # Defensive copy to avoid modifying original enum list
    weighted_choices = available_choices.copy()
    for item in weight:
        if item not in available_choices:
            logger.warning(f"Weight provided for invalid enum item: {item}")
            continue
        weighted_choices.extend([item] * weight[item])

    selected = secrets.choice(weighted_choices)
    logger.info(f"Selected {selected} from enum with weights")
    return selected


T = TypeVar('T')


def random_from_list(
    data: List[T],
    weight: Optional[Dict[T, int]] = None
) -> T:
    logger.debug(f"Random selection from list called with data: {data} and weights: {weight}")

    if weight is None:
        selected = secrets.choice(data)
        # logger.info(f"Selected {selected} from list without weights")
        return selected

    # Defensive copy to avoid modifying original list
    weighted_choices = data.copy()
    for item in weight:
        if item not in data:
            logger.warning(f"Weight provided for item not in list: {item}")
            continue
        weighted_choices.extend([item] * weight[item])

    selected = secrets.choice(weighted_choices)
    logger.info(f"Selected {selected} from list with weights")
    return selected
