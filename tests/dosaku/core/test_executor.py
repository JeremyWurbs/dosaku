import logging
import pytest
from unittest.mock import patch

from dosaku import Config, Executor
from dosaku.utils import default_logger


class ExecutorTest:
    def __init__(self):
        self.instance = self.init_executor()
        self.instance.logger = default_logger(
            name=__name__,
            file_level=logging.DEBUG,
            file_name=Config()['FILE_PATHS']['UNITTEST_LOGS'])

    @patch.multiple(Executor, __abstractmethods__=set())
    def init_executor(self):
        instance = Executor()
        return instance

    def __enter__(self):
        return self.instance

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.instance.__exit__(exc_type, exc_val, exc_tb)


def test_executor():
    with ExecutorTest() as executor:
        assert executor.is_executor is True
