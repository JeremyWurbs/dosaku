from configparser import ConfigParser, ExtendedInterpolation
import json
import os


class Config:
    def __init__(self, config_path: str = None):
        self.config = ConfigParser(interpolation=ExtendedInterpolation())

        if config_path is None:
            __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
            config_path = os.path.join(__location__, 'config.ini')

        if not os.path.exists(config_path):
            raise FileNotFoundError(f'No such file "{config_path}".')

        self.config.read(config_path)

        for section in self.config.sections():
            for (k, v) in self.config.items(section):
                if v[0] == '~':
                    self.config[section][k] = v.replace('~', os.path.expanduser('~'))

    def __getitem__(self, item):
        return self.config[item]

    def __str__(self):
        return str({section: dict(self.config[section]) for section in self.config.sections()}).replace("\'", "\"")

    def as_dict(self):
        return json.loads(self.__str__())
