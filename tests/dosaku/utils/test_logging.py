import logging
import os

from dosaku.utils import logger


def test_logger():
    logger_ = logger(name='Dosaku',
                     stream_level=logging.DEBUG,
                     file_level=logging.DEBUG,
                     file_name='test_logs.txt')

    logger_.debug('debug log')
    logger_.info('info log')
    logger_.warning('warning log')
    logger_.error('error log')
    logger_.critical('critical log')

    assert os.path.exists('test_logs.txt')
