import logging
from unittest.mock import patch

from dosaku import Config, Service
from dosaku.utils import default_logger


class ServiceTest:
    def __init__(self):
        self.instance = self.init_module()
        self.instance.logger = default_logger(
            name=__name__,
            file_level=logging.DEBUG,
            file_name=Config()['FILE_PATHS']['UNITTEST_LOGS'])

    @patch.multiple(Service, __abstractmethods__=set())
    def init_module(self):
        instance = Service()
        return instance

    def __enter__(self):
        return self.instance

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.instance.__exit__(exc_type, exc_val, exc_tb)


def test_service():
    with ServiceTest() as service:
        assert service.is_service is True
