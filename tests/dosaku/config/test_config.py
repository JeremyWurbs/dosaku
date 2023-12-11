"""Unit test methods for dosaku.config.config.Config class."""
import os
import pytest

from dosaku import Config


def test_functionality():
    config = Config()
    assert isinstance(str(config), str)
    assert isinstance(config.pretty_print(), str)
    assert isinstance(config.as_dict(), dict)


def test_configuration():
    config = Config()
    dirs = (
        config['DIR_PATHS']['ROOT'],
        config['DIR_PATHS']['PACKAGE'],
        config['DIR_PATHS']['DATA'],
        config['DIR_PATHS']['MODELS'],
        config['DIR_PATHS']['APPS'],
        config['DIR_PATHS']['LOGS'],
    )
    for dir in dirs:
        assert os.path.isdir(dir)


def test_config_not_found():
    with pytest.raises(Exception):
        config = Config('/this/config/path/does/not/exist/config.ini')
        isinstance(config, Config)
