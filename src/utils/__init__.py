from typing import List, Optional, TypeVar

from .hybrid import hybrid_property

DictItem = TypeVar("DictItem")


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


# TODO this should be moved to drizm_commons

class IterableKeyDictionary(dict):
    __slots__ = ["__weakref__"]
    __doc__ = ""

    def __getitem__(self, item) -> Optional[DictItem]:
        for k in [k for k in self.keys() if type(k) is tuple or list]:
            if item in k:
                return super().__getitem__(k)
        raise KeyError(f"Key '{k}' not found.")


__all__ = [
    "hybrid_property",
    "find_index_by_value_at_key",
    "IterableKeyDictionary"
]
