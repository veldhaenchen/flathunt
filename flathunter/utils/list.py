"""Utility type for chunking lists"""

from typing import List
from typing import TypeVar

CLT = TypeVar("CLT")


def chunk_list(list_var: List[CLT], size: int) -> List[CLT]:
    """
    split a list into the given chunk size
    :param l: input list
    :param size: output chunk size
    :return:
    """
    for i in range(0, len(list_var), size):
        yield list_var[i:i + size]
