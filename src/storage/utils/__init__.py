from typing import List, Optional

from .hybrid import hybrid_property


def find_index_by_value_at_key(items: List[dict],
                               key,
                               value) -> Optional[int]:
    """
    Inside of a list of dictionaries,
    find the index of the first dictionary,
    that has a matching value for the given key
    """
    for index, item in enumerate(items):
        if item.get(key) == value:
            return index
    return None


__all__ = ["hybrid_property", "find_index_by_value_at_key"]
