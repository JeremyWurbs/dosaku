import logging

from dosaku import Config


class DosakuBase:
    """Base class for all Dosaku core classes.

    The DosakuBase adds default context manager and logging methods. All Dosaku core classes derive from DosakuBase
    in order to provide consistent associated capabilities throughout the entire dosaku package.
    """
    config = Config()

    def __init__(self, suppress: bool = False):
        self.suppress = suppress
        self._logger = logging.getLogger(self.__module__)
        self.logger.debug(f'Initialized {self.__class__} object with id: {id(self)}.')

    @property
    def unique_name(self) -> str:
        return self.__module__ + '.' + type(self).__name__

    @property
    def name(self) -> str:
        return type(self).__name__

    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, new_logger):
        self._logger = new_logger

    def __enter__(self):
        self.logger.debug({f'Initializing {self.name} as a context manager.'})
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.debug(f'Exiting context manager for {self.name}.')
        if exc_type is not None:
            info = (exc_type, exc_val, exc_tb)
            self.logger.exception("Exception occurred", exc_info=info)
            return self.suppress
        return False
