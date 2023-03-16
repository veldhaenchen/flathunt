"""String utility functions"""
from typing import TypeVar

T = TypeVar('T', str, None)

"""Functions and classes related to processing/manipulating strings"""
def remove_prefix(text: T, prefix: str) -> T:
    """Note that this method can just be replaced by str.removeprefix()
    if the project ever moves to Python 3.9+"""
    if text is None:
        return text
    if text.startswith(prefix):
        return text[len(prefix):]
    return text
