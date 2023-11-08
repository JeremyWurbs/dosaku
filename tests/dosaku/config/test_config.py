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
    assert os.path.isdir(config['PATHS']['ROOT_DIR'])
    assert isinstance(config['PATHS']['PACKAGE_DIR'], str)
    assert isinstance(config['PATHS']['DATA_ROOT'], str)
    assert isinstance(config['PATHS']['MODELS_ROOT'], str)
    assert isinstance(config['PATHS']['APPS_ROOT'], str)


def test_config_not_found():
    with pytest.raises(Exception):
        config = Config('/this/config/path/does/not/exist/config.ini')
        isinstance(config, Config)
