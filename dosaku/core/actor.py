from typing import Optional


class Actor:
    def __init__(self, doc: Optional[str] = None):
        if doc is not None:
            self.__doc__ = doc
