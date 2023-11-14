from __future__ import annotations
from abc import ABC, abstractmethod
import logging


from dosaku import Context
from dosaku.utils import ifnone


class Module(Context, ABC):
    logger = logging.getLogger(__name__)

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    def add_one(self, num: int):
        self.logger.critical('add_one critical message')
        return num + 1
