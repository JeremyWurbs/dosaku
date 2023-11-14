import logging


class Context:
    logger = logging.getLogger(__name__)

    def __init__(self, suppress: bool = False):
        self.suppress = suppress
        print(f'__name__: {__name__}')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            info = (exc_type, exc_val, exc_tb)
            self.logger.exception("Exception occurred", exc_info=info)
            return self.suppress
        return False
