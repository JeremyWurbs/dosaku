import logging
import pytest
from unittest.mock import patch

from dosaku import Config, Module
from dosaku.utils import default_logger


class ModuleTest:
    def __init__(self):
        self.instance = self.init_module()
        self.instance.logger = default_logger(
            name=__name__,
            file_level=logging.DEBUG,
            file_name=Config()['FILE_PATHS']['UNITTEST_LOGS'])

    @patch.multiple(Module, __abstractmethods__=set())
    def init_module(self):
        instance = Module()
        return instance

    def __enter__(self):
        return self.instance

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.instance.__exit__(exc_type, exc_val, exc_tb)


def test_module():
    with ModuleTest() as module:
        assert module.add_one(5) == 6
        with open(Config()['FILE_PATHS']['UNITTEST_LOGS']) as file:
            assert len(file.readlines()) == 1

        with pytest.raises(NotImplementedError):
            print(module.name)
